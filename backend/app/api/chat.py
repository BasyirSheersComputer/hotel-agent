from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from app.services.retrieval import query_rag
from app.services.metrics_service import get_metrics_service
from app.middleware.auth import get_current_user_optional, CurrentUser
from app.config.settings import DEMO_MODE
import time
import os
import re

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    agent_id: str = "default"  # Allow frontend to pass agent ID

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]

# Feature flag for metrics (default: enabled)
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"

def detect_question_category(query_text: str) -> str:
    """
    Automatically detect the category of a question based on keywords.
    """
    query_lower = query_text.lower()
    
    # Category detection patterns (ordered by specificity)
    categories = {
        "Dining": ["restaurant", "food", "meal", "breakfast", "lunch", "dinner", "eat", "menu", "bar", "cuisine", "mutiara", "rembulan", "enak", "pinang"],
        "Room Service": ["room service", "laundry", "housekeeping", "minibar", "towel", "bed", "pillow", "ac", "air conditioning", "wifi", "my room", "suite"],
        "Activities": ["activity", "sport", "pool", "beach", "trapeze", "archery", "kayak", "sailing", "tennis", "gym", "yoga", "spa", "fitness"],
        "Kids & Family": ["kids", "children", "family", "mini club", "baby", "child", "playground"],
        "Location & Transport": ["nearest", "nearby", "closest", "pharmacy", "hospital", "atm", "bank", "petrol", "gas station", "taxi", "grab", "shuttle", "transport", "where can i"],
        "Facilities": ["pool", "gym", "lobby", "reception", "boutique", "parking", "wifi", "facilities"],
        "Spa & Wellness": ["spa", "massage", "wellness", "treatment", "relaxation"],
        "Concierge": ["book", "reservation", "arrange", "help", "assistance", "recommend"]
    }
    
    for category, keywords in categories.items():
        if any(keyword in query_lower for keyword in keywords):
            return category
    
    return "General"

def estimate_tokens_from_text(text: str) -> int:
    """
    Rough estimate of token count (1 token ≈ 4 characters for English).
    """
    return len(text) // 4

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    http_request: Request,
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    start_time = time.time()
    
    # Get tenant context (falls back to demo org in demo mode)
    org_id = getattr(http_request.state, 'org_id', None)
    user_id = current_user.user_id if current_user else None
    
    try:
        result = query_rag(request.query)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log metrics if enabled
        if ENABLE_METRICS:
            try:
                metrics_service = get_metrics_service()
                
                # Determine source type with improved detection
                sources_str = str(result.get("sources", []))
                if "Google Maps" in sources_str or "Maps API" in sources_str:
                    source_type = "Maps"
                else:
                    source_type = "RAG"
                
                # Detect question category
                question_category = detect_question_category(request.query)
                
                # Estimate token usage (prompt + response)
                # This is a rough estimate - for production, extract from LLM response
                prompt_tokens = estimate_tokens_from_text(request.query)
                response_tokens = estimate_tokens_from_text(result.get("answer", ""))
                total_tokens = prompt_tokens + response_tokens
                
                # Estimate cost (GPT-4o pricing: $0.03 per 1K tokens)
                cost_estimate = (total_tokens / 1000) * 0.03
                
                metrics_service.log_query(
                    query_text=request.query,
                    response_time_ms=response_time_ms,
                    question_category=question_category,
                    source_type=source_type,
                    agent_id=request.agent_id,
                    org_id=org_id,
                    success=True,
                    tokens_used=total_tokens,
                    cost_estimate=cost_estimate
                )
            except Exception as metrics_error:
                # Don't fail the request if metrics logging fails
                print(f"Metrics logging error: {metrics_error}")
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log failed query if metrics enabled
        if ENABLE_METRICS:
            try:
                metrics_service = get_metrics_service()
                metrics_service.log_query(
                    query_text=request.query,
                    response_time_ms=response_time_ms,
                    question_category=detect_question_category(request.query),
                    agent_id=request.agent_id,
                    org_id=org_id,
                    success=False,
                    error_message=str(e)
                )
            except Exception as metrics_error:
                print(f"Metrics logging error: {metrics_error}")
        
        raise HTTPException(status_code=500, detail=str(e))
