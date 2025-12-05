from sqlalchemy.orm import Session
from app.models import ChatSession, ChatMessage
from app.services.auth_service import User
from typing import List, Optional
import uuid
from datetime import datetime

class ChatHistoryService:
    @staticmethod
    def create_session(db: Session, user: User, title: str = "New Chat") -> ChatSession:
        """Create a new chat session for the user."""
        session = ChatSession(
            session_id=uuid.uuid4(),
            org_id=user.org_id,
            user_id=user.user_id,
            title=title
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_user_sessions(db: Session, user: User, limit: int = 50) -> List[ChatSession]:
        """Get all chat sessions for a user, ordered by most recent."""
        return db.query(ChatSession).filter(
            ChatSession.user_id == user.user_id,
            ChatSession.org_id == user.org_id
        ).order_by(ChatSession.updated_at.desc()).limit(limit).all()

    @staticmethod
    def get_session(db: Session, session_id, user: User) -> Optional[ChatSession]:
        """Get a specific session, ensuring it belongs to the user."""
        # Convert to UUID if string
        if isinstance(session_id, str):
            session_id = uuid.UUID(session_id)
            
        return db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user.user_id,
            ChatSession.org_id == user.org_id
        ).first()

    @staticmethod
    def add_message(
        db: Session, 
        session_id, 
        role: str, 
        content: str,
        user: User
    ) -> ChatMessage:
        """Add a message to a session."""
        # Convert to UUID if string
        if isinstance(session_id, str):
            session_id = uuid.UUID(session_id)
            
        # Verify session ownership first
        session = ChatHistoryService.get_session(db, session_id, user)
        if not session:
            raise ValueError("Session not found or access denied")

        message = ChatMessage(
            message_id=uuid.uuid4(),
            session_id=session_id,
            org_id=user.org_id,
            role=role,
            content=content
        )
        db.add(message)
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_session_messages(db: Session, session_id, user: User) -> List[ChatMessage]:
        """Get all messages for a session."""
        # Convert to UUID if string
        if isinstance(session_id, str):
            session_id = uuid.UUID(session_id)
            
        # Verify session ownership
        if not ChatHistoryService.get_session(db, session_id, user):
            return []
            
        return db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.asc()).all()

    @staticmethod
    def delete_session(db: Session, session_id, user: User) -> bool:
        """Delete a session and all its messages."""
        # Convert to UUID if string
        if isinstance(session_id, str):
            session_id = uuid.UUID(session_id)
            
        session = ChatHistoryService.get_session(db, session_id, user)
        if not session:
            return False
            
        db.delete(session)
        db.commit()
        return True
