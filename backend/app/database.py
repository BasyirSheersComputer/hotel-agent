"""
Database configuration for multi-tenant SaaS deployment.
Supports both PostgreSQL (production) and SQLite (local dev).
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Database URL from environment (fallback to SQLite for local dev)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./resort_genius.db"  # Local fallback
)

# Use NullPool for serverless environments like Cloud Run
engine = create_database_engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool if "sqlite" not in DATABASE_URL else None,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency for FastAPI routes to get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def set_tenant_context(connection, org_id: str):
    """
    Set tenant context for Row-Level Security (PostgreSQL only).
    """
    if "postgresql" in DATABASE_URL:
        connection.execute(f"SET app.current_org_id = '{org_id}'")

# PostgreSQL-specific: Enable RLS on connection
if "postgresql" in DATABASE_URL:
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """
        Called on each new database connection.
        Can be used to set session parameters.
        """
        pass  # RLS context set per-request in middleware
