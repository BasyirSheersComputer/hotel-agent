import sys
from pathlib import Path

# Add backend directory to path so we can import app modules
sys.path.append(str(Path(__file__).parent.resolve()))

import sqlite3
import os
from sqlalchemy import create_engine, text
from app.config.settings import DATABASE_URL
from app.database import Base

def clean_analytics_db():
    db_path = Path("backend/analytics.db").resolve()
    if path := db_path if db_path.exists() else Path("analytics.db").resolve():
        if path.exists():
            print(f"Cleaning Analytics DB: {path}")
            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM queries")
                cursor.execute("DELETE FROM conversions")
                cursor.execute("DELETE FROM agents")
                cursor.execute("DELETE FROM performance_snapshots")
                conn.commit()
                conn.close()
                print("Analytics DB cleaned.")
            except Exception as e:
                print(f"Error cleaning analytics DB: {e}")
        else:
            print("Analytics DB not found.")

def clean_main_db():
    print("Cleaning Main DB...")
    try:
        # Create engine from DATABASE_URL
        # Note: DATABASE_URL is loaded from .env/Secrets by settings.py
        # Ensure env is loaded
        from app.env_utils import load_env_robustly
        load_env_robustly()
        
        # We need to import DATABASE_URL again after loading env?
        # settings.py loads env at module level.
        # But let's verify.
        
        engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///./resort_genius.db"))
        
        with engine.connect() as conn:
            # Disable FK checks for SQLite
            if "sqlite" in str(engine.url):
                conn.execute(text("PRAGMA foreign_keys = OFF"))
            
            conn.execute(text("DELETE FROM chat_messages"))
            conn.execute(text("DELETE FROM chat_sessions"))
            
            conn.commit()
            print("Main DB cleaned.")
            
    except Exception as e:
        print(f"Error cleaning Main DB: {e}")

if __name__ == "__main__":
    clean_analytics_db()
    clean_main_db()
