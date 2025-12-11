"""
Multi-tenant data models for SaaS deployment.
All tables include org_id for tenant isolation.
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, DECIMAL, UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
import uuid
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type for PostgreSQL,
    CHAR(36) for others (SQLite, etc), storing as stringified UUIDs.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(str(value)))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(str(value))
            else:
                return value

UUIDType = GUID
from app.database import Base, DATABASE_URL

class Organization(Base):
    """
    Tenant/Organization table.
    Each hotel/resort is an organization.
    """
    __tablename__ = "organizations"
    __table_args__ = {'extend_existing': True}
    
    org_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    plan = Column(String(50), default="free")  # free, pro, enterprise
    max_users = Column(Integer, default=10)
    max_kb_docs = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(JSON, default={})
    
    # Billing / Stripe
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    billing_account_id = Column(UUIDType, ForeignKey("billing_accounts.account_id"), nullable=True)
    subscription_status = Column(String(50), default="free") # free, active, past_due, canceled
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    sessions = relationship("ChatSession", back_populates="organization", cascade="all, delete-orphan")
    kb_documents = relationship("KBDocument", back_populates="organization", cascade="all, delete-orphan")
    billing_account = relationship("BillingAccount", back_populates="organizations")

class BillingAccount(Base):
    """
    Billing Account table.
    """
    __tablename__ = "billing_accounts"
    __table_args__ = {'extend_existing': True}
    
    account_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    billing_email = Column(String(255))
    billing_name = Column(String(255))
    balance = Column(DECIMAL(10, 2), default=0.00)
    currency = Column(String(3), default="MYR")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organizations = relationship("Organization", back_populates="billing_account")
    subscriptions = relationship("Subscription", back_populates="billing_account", cascade="all, delete-orphan")

class Subscription(Base):
    """
    Subscription table.
    """
    __tablename__ = "subscriptions"
    __table_args__ = {'extend_existing': True}
    
    sub_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    account_id = Column(UUIDType, ForeignKey("billing_accounts.account_id", ondelete="CASCADE"), nullable=False, index=True)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    plan_id = Column(String(50), nullable=False) # e.g. pro_monthly
    status = Column(String(50), default="active") # active, past_due, canceled
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    billing_account = relationship("BillingAccount", back_populates="subscriptions")


class Property(Base):
    """
    Property table (Hotel/Resort).
    Belongs to an Organization.
    """
    __tablename__ = "properties"
    __table_args__ = {'extend_existing': True}
    
    property_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    address = Column(String(255))
    timezone = Column(String(50), default="UTC")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(JSON, default={})
    
    # Relationships
    organization = relationship("Organization", back_populates="properties")
    users = relationship("User", back_populates="property")
    sessions = relationship("ChatSession", back_populates="property")
    kb_documents = relationship("KBDocument", back_populates="property")

# Organization Updates (add relationship)
Organization.properties = relationship("Property", back_populates="organization", cascade="all, delete-orphan")

class User(Base):
    """
    User table (tenant-scoped).
    """
    __tablename__ = "users"
    
    user_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(UUIDType, ForeignKey("properties.property_id", ondelete="SET NULL"), nullable=True, index=True) # Optional link to specific property
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    role = Column(String(50), default="agent")  # super_admin, tenant_admin, property_manager, agent, viewer
    language_pref = Column(String(10), default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Password Reset
    reset_token = Column(String(100), nullable=True, index=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    property = relationship("Property", back_populates="users")
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        {"schema": None, "extend_existing": True}
    )

class ChatSession(Base):
    """
    Chat session table (tenant-scoped).
    """
    __tablename__ = "chat_sessions"
    __table_args__ = {'extend_existing': True}
    
    session_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(UUIDType, ForeignKey("properties.property_id", ondelete="CASCADE"), nullable=True, index=True) # Optional if org-wide
    user_id = Column(UUIDType, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="sessions")
    property = relationship("Property", back_populates="sessions")
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """
    Chat message table (tenant-scoped).
    """
    __tablename__ = "chat_messages"
    __table_args__ = {'extend_existing': True}
    
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
    __table_args__ = {'extend_existing': True}
    
    doc_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(UUIDType, ForeignKey("properties.property_id", ondelete="CASCADE"), nullable=True, index=True) # Optional (Global vs Local)
    filename = Column(String(255), nullable=False)
    file_url = Column(Text, nullable=False)
    content_hash = Column(String(64))
    uploaded_by = Column(UUIDType, ForeignKey("users.user_id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="processing")
    
    # Relationships
    organization = relationship("Organization", back_populates="kb_documents")
    property = relationship("Property", back_populates="kb_documents")

class Query(Base):
    """
    Analytics query table (tenant-scoped).
    """
    __tablename__ = "queries"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(UUIDType, ForeignKey("properties.property_id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(UUIDType, ForeignKey("users.user_id"))
    session_id = Column(UUIDType, ForeignKey("chat_sessions.session_id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    query_text = Column(Text, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    question_category = Column(String(100))
    source_type = Column(String(50))
    agent_id = Column(String(255))
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    tokens_used = Column(Integer, default=0)
    cost_estimate = Column(DECIMAL(10, 6), default=0.0)
    accuracy_score = Column(DECIMAL(3, 2), default=0.0)
    aht_saved_s = Column(Integer, default=0)
    
    # Efficiency Quadrant
    hold_time_ms = Column(Integer, default=0)
    escalation_needed = Column(Boolean, default=False)
    
    # Accuracy & Quality Quadrant
    is_sop_compliant = Column(Boolean, default=True)
    correct_on_first_try = Column(Boolean, default=True)
    
    # Revenue Quadrant
    booking_intent = Column(Boolean, default=False)
    upsell_intent = Column(Boolean, default=False)
    revenue_potential = Column(DECIMAL(10, 2), default=0.00)
    
    # CSAT Quadrant
    sentiment_score = Column(DECIMAL(3, 2), default=0.0) # -1.0 to 1.0
    csat_rating = Column(Integer, default=5) # 1-5

class KBEmbedding(Base):
    """
    Embeddings table for pgvector (tenant-scoped).
    """
    __tablename__ = "kb_embeddings"
    __table_args__ = {'extend_existing': True}
    
    embedding_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(UUIDType, ForeignKey("properties.property_id", ondelete="CASCADE"), nullable=True, index=True) # Optional
    doc_id = Column(UUIDType, ForeignKey("kb_documents.doc_id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    # embedding = Column(Vector(1536))
    meta_data = Column(JSONB if "postgresql" in DATABASE_URL else Text)

class AgentMetric(Base):
    """
    Agent performance metrics (tenant-scoped).
    """
    __tablename__ = "agent_metrics"
    __table_args__ = {'extend_existing': True}
    
    agent_id = Column(String(255), primary_key=True)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    property_id = Column(UUIDType, ForeignKey("properties.property_id", ondelete="CASCADE"), nullable=True, index=True)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    total_queries = Column(Integer, default=0)

class PerformanceSnapshot(Base):
    """
    Hourly performance snapshots (tenant-scoped).
    """
    __tablename__ = "performance_snapshots"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(UUIDType, ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(UUIDType, ForeignKey("properties.property_id", ondelete="CASCADE"), nullable=True, index=True)
    snapshot_time = Column(DateTime(timezone=True), server_default=func.now())
    total_queries = Column(Integer)
    avg_response_time_ms = Column(DECIMAL(10, 2))
    success_rate = Column(DECIMAL(5, 2))
    unique_agents = Column(Integer)
