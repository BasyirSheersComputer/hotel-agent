
import os
import sys
import logging
from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from app.models import * # Import all models to ensure registry is populated

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
SQLITE_DB_PATH = "./resort_genius.db" # Default local path
POSTGRES_DB_URL = "postgresql://postgres:password@localhost:5432/hotel_agent"

def migrate():
    # 1. Connect to Source (SQLite)
    source_url = f"sqlite:///{SQLITE_DB_PATH}"
    logger.info(f"Connecting to Source: {source_url}")
    source_engine = create_engine(source_url)
    
    if not os.path.exists(SQLITE_DB_PATH):
        logger.error(f"Source database file not found: {SQLITE_DB_PATH}")
        return

    # 2. Connect to Target (PostgreSQL)
    logger.info(f"Connecting to Target: {POSTGRES_DB_URL}")
    try:
        target_engine = create_engine(POSTGRES_DB_URL)
        target_conn = target_engine.connect()
        target_conn.close()
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        logger.error("Is Docker running? (docker-compose up -d)")
        return

    # 3. Create Schema in Target
    logger.info("Creating schema in PostgreSQL...")
    # Drop all tables first to ensure clean state (Optional - be careful in prod!)
    # Base.metadata.drop_all(target_engine) 
    Base.metadata.create_all(target_engine)
    logger.info("Schema created.")

    # 4. Migrate Data
    SessionSource = sessionmaker(bind=source_engine)
    SessionTarget = sessionmaker(bind=target_engine)
    
    source_session = SessionSource()
    target_session = SessionTarget()
    
    tables_order = [
         Organization, 
         User, 
         ChatSession, 
         ChatMessage, 
         KBDocument, 
         Query, 
         AgentMetric, 
         PerformanceSnapshot
         # KBEmbedding skipped as it's likely empty or specialized
    ]
    
    try:
        for model in tables_order:
            table_name = model.__tablename__
            logger.info(f"Migrating table: {table_name}...")
            
            # Clear target table
            target_session.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
            target_session.commit()
            
            # Fetch from source
            rows = source_session.query(model).all()
            count = len(rows)
            logger.info(f"Found {count} rows in {table_name}")
            
            if count > 0:
                # Insert to target
                # We need to detach objects from source session to add to target
                # Or verify if merge/add works across sessions.
                # Easiest is to make new instances or use expunge.
                for row in rows:
                    source_session.expunge(row)
                    target_session.merge(row) # merge handles potential PK conflicts/updates
                    
                target_session.commit()
                logger.info(f"Migrated {unmigrated_count if 'unmigrated_count' in locals() else count} rows.")

            # Inject Defaults if missing (Fix for Orphaned Data)
            # ID: 00000000-0000-0000-0000-000000000001
            import uuid
            default_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
            
            if table_name == "organizations":
                 # Check if default exists or if table is empty
                 if target_session.query(Organization).count() == 0:
                     logger.info("Injecting Default Organization (Fixing Orphans)...")
                     def_org = Organization(org_id=default_id, name="Demo Resort", slug="demo-hotel", plan="enterprise")
                     target_session.add(def_org)
                     target_session.commit()
            
            if table_name == "users":
                 if target_session.query(User).count() == 0:
                     logger.info("Injecting Default User (Fixing Orphans)...")
                     def_user = User(user_id=default_id, org_id=default_id, email="demo@resort-genius.com", password_hash="$pbkdf2-sha256$29000$5NybU2otpTQGoNS6t5YSgg$r83pJzmkkZ4MSucoqy1ePwzQfi5ZxWPdWUnIIiHAggog", name="Demo Admin", role="admin")
                     target_session.add(def_user)
                     target_session.commit()
            
        logger.info("Migration Connection Successful!")

        # 5. Verification
        logger.info("Verifying counts...")
        for model in tables_order:
            src_count = source_session.query(model).count()
            tgt_count = target_session.query(model).count()
            if src_count == tgt_count:
                logger.info(f"✓ {model.__tablename__}: {tgt_count}/{src_count} match.")
            else:
                logger.error(f"✗ {model.__tablename__}: {tgt_count} (Target) != {src_count} (Source)")
                
    except Exception as e:
        logger.error(f"Migration Failed: {e}")
        target_session.rollback()
    finally:
        source_session.close()
        target_session.close()

if __name__ == "__main__":
    migrate()
