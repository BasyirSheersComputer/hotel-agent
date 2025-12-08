from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
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
import asyncio
from concurrent.futures import ThreadPoolExecutor

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

async def run_sync_in_executor(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
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
            detected_lang = await run_sync_in_executor(detect_language, request.query)
            user_language = detected_lang
        else:
            detected_lang = user_language
        
        # If query is not in English, translate for RAG processing
        if user_language != "en":
            # returns tuple (text, lang)
            translation_result = await run_sync_in_executor(translate_to_english, request.query)
            query_for_rag = translation_result[0]
        
        # Pass org_id for tenant-scoped knowledge base retrieval
        # Now awaiting the ASYNC query_rag
        result = await query_rag(query_for_rag, org_id=org_id)
        
        # Translate response back to user's language if not English
        answer = result["answer"]
        if user_language and user_language != "en":
            answer = await run_sync_in_executor(translate_response, answer, user_language)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log metrics in background
        if ENABLE_METRICS:
            try:
                metrics_service = get_metrics_service()
                
                # Determine source type
                sources_str = str(result.get("sources", []))
                if "Google Maps" in sources_str or "Maps API" in sources_str:
                    source_type = "Maps"
                else:
                    source_type = "RAG"
                
                # Detect question category
                question_category = detect_question_category(request.query)
                
                # Estimate token usage
                prompt_tokens = estimate_tokens_from_text(request.query)
                response_tokens = estimate_tokens_from_text(result.get("answer", ""))
                total_tokens = prompt_tokens + response_tokens
                cost_estimate = (total_tokens / 1000) * 0.03
                
                # Intent & Sentiment Analysis (Heuristic Rule-Based)
                query_lower = request.query.lower()
                answer_lower = answer.lower()
                
                # Booking Intent
                booking_keywords = ["book", "reservation", "reserve", "price", "cost", "availability", "check-in", "stay"]
                booking_intent = any(k in query_lower for k in booking_keywords)
                
                # Upsell Intent
                upsell_keywords = ["upgrade", "suite", "premium", "private", "luxury", "spa package", "romantic dinner"]
                upsell_intent = any(k in query_lower for k in upsell_keywords)
                
                # Revenue Potential Estimate
                revenue_potential = 0.0
                if booking_intent:
                    revenue_potential += 1500.00 # Avg booking value
                if upsell_intent:
                    revenue_potential += 300.00 # Avg upsell value
                
                # Sentiment Analysis (Basic)
                sentiment_score = 0.0
                positive_words = ["thank", "great", "good", "helpful", "amazing", "perfect", "excellent"]
                negative_words = ["bad", "wrong", "useless", "confusing", "error", "stupid"]
                
                if any(w in query_lower for w in positive_words):
                    sentiment_score += 0.5
                if any(w in query_lower for w in negative_words):
                    sentiment_score -= 0.5
                    
                csat_rating = 5 if sentiment_score >= 0 else 3
                
                # SOP Compliance (Simulated based on RAG usage)
                is_sop_compliant = True if result.get("sources") else False
                
                # Examples in prompt...
                
                # SOP Compliance (Simulated based on RAG usage)
                is_sop_compliant = True if result.get("sources") else False
                
                # Add to background tasks (non-blocking)
                background_tasks.add_task(
                    metrics_service.log_query,
                    query_text=request.query,
                    response_time_ms=response_time_ms,
                    question_category=question_category,
                    source_type=source_type,
                    agent_id=request.agent_id,
                    org_id=org_id,
                    success=True,
                    tokens_used=total_tokens,
                    cost_estimate=cost_estimate,
                    # New Metrics
                    hold_time_ms=0, # Near zero for AI
                    escalation_needed=False, # Default
                    is_sop_compliant=is_sop_compliant,
                    correct_on_first_try=True, # Assessing as true if successful response
                    booking_intent=booking_intent,
                    upsell_intent=upsell_intent,
                    revenue_potential=revenue_potential,
                    sentiment_score=sentiment_score,
                    csat_rating=csat_rating
                )
            except Exception as metrics_error:
                print(f"Metrics scheduling error: {metrics_error}")
        
        # Save to history (Sync, but fast enough relative to RAG)
        session_id = request.session_id
        if current_user:
            try:
                if not session_id:
                    title = request.query[:50] + "..." if len(request.query) > 50 else request.query
                    session = ChatHistoryService.create_session(db, current_user, title)
                    session_id = str(session.session_id)
                
                ChatHistoryService.add_message(
                    db, session_id, "user", request.query, current_user
                )
                ChatHistoryService.add_message(
                    db, session_id, "agent", answer, current_user
                )
            except Exception as history_error:
                print(f"History saving error: {history_error}")
                if not session_id:
                    session_id = str(uuid.uuid4())
 
        return ChatResponse(
            answer=answer,
            sources=result["sources"],
            detected_language=detected_lang,
            session_id=session_id or str(uuid.uuid4())
        )
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log failed query in background
        if ENABLE_METRICS:
            metrics_service = get_metrics_service()
            background_tasks.add_task(
                metrics_service.log_query,
                query_text=request.query,
                response_time_ms=response_time_ms,
                question_category=detect_question_category(request.query),
                agent_id=request.agent_id,
                org_id=org_id,
                success=False,
                error_message=str(e)
            )
        
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

