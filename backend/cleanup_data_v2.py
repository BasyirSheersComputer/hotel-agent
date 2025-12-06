import sqlite3
import os
from pathlib import Path

def clean_dbs():
    # Only using resort_genius.db (MAIN DB) now
    main_db_path = Path("resort_genius.db").resolve()
    if main_db_path.exists():
        print(f"Cleaning Main DB: {main_db_path}")
        try:
            conn = sqlite3.connect(main_db_path)
            cursor = conn.cursor()
            
            # List of tables to clear
            tables = [
                "queries", 
                "agent_metrics", 
                "performance_snapshots",
                "chat_messages", 
                "chat_sessions"
            ]
            
            for table in tables:
                try:
                    cursor.execute(f"DELETE FROM {table}")
                    print(f"  Cleared {table}")
                except Exception as e:
                    print(f"  Failed (maybe missing): {table} - {e}")
            
            conn.commit()
            conn.close()
            print("Database cleaned.")
        except Exception as e:
            print(f"Error cleaning DB: {e}")
    else:
        print(f"Main DB not found at {main_db_path}")
        
    # Remove old analytics.db if exists to avoid confusion
    analytics_path = Path("analytics.db").resolve()
    if analytics_path.exists():
        try:
            os.remove(analytics_path)
            print("Removed obsolete analytics.db")
        except:
            pass

if __name__ == "__main__":
    clean_dbs()
