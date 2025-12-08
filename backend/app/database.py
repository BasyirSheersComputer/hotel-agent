"""
Database configuration for multi-tenant SaaS deployment.
Supports both PostgreSQL (production) and SQLite (local dev).
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

# Database URL from environment (fallback to SQLite for local dev)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./resort_genius.db"  # Local fallback
)
print(f"DATABASE_URL: {DATABASE_URL[:50]}...")  # Debug: show first 50 chars

# Use NullPool for serverless environments like Cloud Run
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False, "timeout": 60} # 60s timeout

# Configure Connection Pooling
# Default to NullPool for serverless scalability, but allow Pooling for performance/VM deployments (Optimized 3 - PG Selected)
engine_kwargs = {
    "connect_args": connect_args
}

if "sqlite" in DATABASE_URL:
    engine_kwargs["poolclass"] = None
elif os.getenv("DB_POOL_ENABLED", "false").lower() == "true":
    engine_kwargs["poolclass"] = QueuePool
    engine_kwargs["pool_size"] = 40
    engine_kwargs["max_overflow"] = 60
else:
    engine_kwargs["poolclass"] = NullPool

engine = create_engine(DATABASE_URL, **engine_kwargs)

# Enable WAL mode for SQLite
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency for FastAPI routes to get database session.
    """
    print("get_db: Creating Session...")
    db = SessionLocal()
    print("get_db: Session Created. Yielding...")
    try:
        yield db
    finally:
        print("get_db: Closing Session.")
        db.close()

def set_tenant_context(connection, org_id: str):
    """
    Set tenant context for Row-Level Security (PostgreSQL only).
    """
    if "postgresql" in DATABASE_URL:
        connection.execute(f"SET app.current_org_id = '{org_id}'")

# PostgreSQL-specific: Enable RLS on connection
from app.core.context import get_tenant_id

def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """
    Called when a connection is retrieved from the pool.
    Sets the application user/tenant for RLS.
    """
    org_id = get_tenant_id()
    cursor = dbapi_conn.cursor()
    
    if org_id:
        # Set variable for RLS policies
        cursor.execute(f"SET app.current_org_id = '{org_id}'")
    else:
        # Reset variable if no tenant (e.g. public routes or background tasks)
        # This prevents leaking context from previous user in pooled connection
        cursor.execute("SET app.current_org_id = ''")
        
    cursor.close()

if "postgresql" in DATABASE_URL:
    event.listen(engine, "checkout", receive_checkout)
