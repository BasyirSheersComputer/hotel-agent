from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.middleware.auth import get_current_user, CurrentUser, require_agent_or_admin
from app.services.chat_history_service import ChatHistoryService
from pydantic import BaseModel
from datetime import datetime

# All history routes require agent or admin role
router = APIRouter(prefix="/api/history", tags=["Chat History"], dependencies=[Depends(require_agent_or_admin())])

# Pydantic models
class ChatSessionResponse(BaseModel):
    session_id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatMessageResponse(BaseModel):
    message_id: uuid.UUID
    role: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True

class CreateSessionRequest(BaseModel):
    title: str = "New Chat"

class SaveMessageRequest(BaseModel):
    session_id: uuid.UUID
    role: str
    content: str

@router.post("/session", response_model=ChatSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    return ChatHistoryService.create_session(db, current_user, request.title)

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_sessions(
    limit: int = 50,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all chat sessions for the current user."""
    return ChatHistoryService.get_user_sessions(db, current_user, limit)

@router.get("/session/{session_id}", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages for a specific session."""
    try:
        messages = ChatHistoryService.get_session_messages(db, session_id, current_user)
        # If no messages found, check if session exists to distinguish between empty and 404
        if not messages:
            session = ChatHistoryService.get_session(db, session_id, current_user)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        return messages
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("ERROR in get_session_messages:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/message", response_model=ChatMessageResponse)
async def save_message(
    request: SaveMessageRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a message to a session."""
    try:
        return ChatHistoryService.add_message(
            db, 
            request.session_id, 
            request.role, 
            request.content, 
            current_user
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/session/{session_id}")
async def delete_session(
    session_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session."""
    success = ChatHistoryService.delete_session(db, session_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "message": "Session deleted"}
