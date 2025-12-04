"""
Multi-tenant data models for SaaS deployment.
All tables include org_id for tenant isolation.
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, DECIMAL, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
import uuid
from app.database import Base

# Use PostgreSQL UUID if available, otherwise string for SQLite
try:
    UUIDType = PG_UUID(as_uuid=True)
except:
    UUIDType = String(36)

class Organization(Base):
    """
    Tenant/Organization table.
    Each hotel/resort is an organization.
    """
    __tablename__ = "organizations"
    
    org_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    plan = Column(String(50), default="free")  # free, pro, enterprise
    max_users = Column(Integer, default=10)
    max_kb_docs = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(JSONB if "postgresql" in Base.metadata.bind.url.drivername else Text, default={})
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    sessions = relationship("ChatSession", back_populates="organization", cascade="all, delete-orphan")
    kb_documents = relationship("KBDocument", back_populates="organization", cascade="all, delete-orphan")

class User(Base):
    """
    User table (tenant-scoped).
    """
    __tablename__ = "users"
    
    user_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    role = Column(String(50), default="agent")  # admin, agent, viewer
    language_pref = Column(String(10), default="en")  # For multi-language support
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique email per organization
        {"schema": None}  # Will add unique constraint in Alembic migration
    )

class ChatSession(Base):
    """
    Chat session table (tenant-scoped).
    """
    __tablename__ = "chat_sessions"
    
    session_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUIDType, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="sessions")
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """
    Chat message table (tenant-scoped).
    """
    __tablename__ = "chat_messages"
    
    message_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    session_id = Column(UUIDType, ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

class KBDocument(Base):
    """
    Knowledge Base document table (tenant-scoped).
    """
    __tablename__ = "kb_documents"
    
    doc_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_url = Column(Text, nullable=False)  # Cloud storage URL
    content_hash = Column(String(64))  # SHA-256 for deduplication
    uploaded_by = Column(UUIDType, ForeignKey("users.user_id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="processing")  # processing, active, failed
    
    # Relationships
    organization = relationship("Organization", back_populates="kb_documents")

class Query(Base):
    """
    Analytics query table (tenant-scoped).
    Enhanced version of previous metrics table.
    """
    __tablename__ = "queries"
    
    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUIDType, ForeignKey("users.user_id"))
    session_id = Column(UUIDType, ForeignKey("chat_sessions.session_id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    query_text = Column(Text, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    question_category = Column(String(100))
    source_type = Column(String(50))
    agent_id = Column(String(255))  # Legacy field, use user_id instead
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    tokens_used = Column(Integer, default=0)
    cost_estimate = Column(DECIMAL(10, 6), default=0.0)
    accuracy_score = Column(DECIMAL(3, 2), default=0.0)
    aht_saved_s = Column(Integer, default=0)

class KBEmbedding(Base):
    """
    Embeddings table for pgvector (tenant-scoped).
    """
    __tablename__ = "kb_embeddings"
    
    embedding_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    doc_id = Column(UUIDType, ForeignKey("kb_documents.doc_id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    # embedding column will be added via Alembic migration with pgvector type
    # embedding = Column(Vector(1536))  # For OpenAI text-embedding-3-small
    metadata = Column(JSONB if "postgresql" in Base.metadata.bind.url.drivername else Text)
