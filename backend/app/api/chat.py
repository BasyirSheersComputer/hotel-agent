from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from app.services.retrieval import query_rag
from app.services.metrics_service import get_metrics_service
from app.services.translation_service import (
    detect_language, translate_to_english, translate_response,
    get_supported_languages, SUPPORTED_LANGUAGES
)
from app.middleware.auth import get_current_user_optional, CurrentUser, require_agent_or_admin
from app.config.settings import DEMO_MODE
from app.services.chat_history_service import ChatHistoryService
from app.database import get_db
from sqlalchemy.orm import Session
import time
import os
import re
import uuid

# Chat requires agent or admin role (demo mode gets admin by default)
router = APIRouter(dependencies=[Depends(require_agent_or_admin())])

class ChatRequest(BaseModel):
    query: str
    agent_id: str = "default"  # Allow frontend to pass agent ID
    language: Optional[str] = None  # User's preferred language (auto-detect if None)
    session_id: Optional[str] = None  # Optional session ID to continue conversation

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    detected_language: Optional[str] = None
    session_id: str  # Return session ID so frontend can continue conversation

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
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    
    # Get tenant context (falls back to demo org in demo mode)
    org_id = getattr(http_request.state, 'org_id', None)
    user_id = current_user.user_id if current_user else None
    
    try:
        # Detect or use provided language
        user_language = request.language
        query_for_rag = request.query
        detected_lang = None
        
        # If language not provided, auto-detect and translate if needed
        if not user_language:
            detected_lang = detect_language(request.query)
            user_language = detected_lang
        else:
            detected_lang = user_language
        
        # If query is not in English, translate for RAG processing
        if user_language != "en":
            query_for_rag, _ = translate_to_english(request.query)
        
        # Pass org_id for tenant-scoped knowledge base retrieval
        result = query_rag(query_for_rag, org_id=org_id)
        
        # Translate response back to user's language if not English
        answer = result["answer"]
        if user_language and user_language != "en":
            answer = translate_response(answer, user_language)
        
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
        
        # Save to history if user is authenticated
        session_id = request.session_id
        if current_user:
            try:
                # Create session if needed
                if not session_id:
                    # Generate a title from the first query (truncate to 50 chars)
                    title = request.query[:50] + "..." if len(request.query) > 50 else request.query
                    session = ChatHistoryService.create_session(db, current_user, title)
                    session_id = str(session.session_id)
                
                # Save user message
                ChatHistoryService.add_message(
                    db, session_id, "user", request.query, current_user
                )
                
                # Save assistant message
                ChatHistoryService.add_message(
                    db, session_id, "agent", answer, current_user
                )
            except Exception as history_error:
                print(f"History saving error: {history_error}")
                # Don't fail the request if history saving fails, but log it
                # If session creation failed, we might return without session_id
                if not session_id:
                    session_id = str(uuid.uuid4()) # Fallback to random ID if DB fails

        return ChatResponse(
            answer=answer,
            sources=result["sources"],
            detected_language=detected_lang,
            session_id=session_id or str(uuid.uuid4())
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


@router.get("/languages")
async def get_languages():
    """
    Get list of supported languages for the UI.
    """
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in SUPPORTED_LANGUAGES.items()
        ],
        "default": "en"
    }

