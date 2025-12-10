
import sqlite3
import os
import sys

# Define expected schema additions
# Table -> {Column: Type}
SCHEMA_CHANGES = {
    "users": {
        "property_id": "CHAR(32)", 
        "last_login": "DATETIME",
        "language_pref": "VARCHAR(10)",
        "reset_token": "VARCHAR(100)",
        "reset_token_expires": "DATETIME"
    },
    "chat_sessions": {
        "property_id": "CHAR(32)"
    },
    "kb_documents": {
        "property_id": "CHAR(32)"
    },
    "agent_metrics": {
        "property_id": "CHAR(32)"
    },
    "performance_snapshots": {
        "property_id": "CHAR(32)"
    },
    "queries": {
        "property_id": "CHAR(32)",
        "hold_time_ms": "INTEGER DEFAULT 0",
        "escalation_needed": "BOOLEAN DEFAULT 0",
        "is_sop_compliant": "BOOLEAN DEFAULT 1",
        "correct_on_first_try": "BOOLEAN DEFAULT 1",
        "booking_intent": "BOOLEAN DEFAULT 0",
        "upsell_intent": "BOOLEAN DEFAULT 0",
        "revenue_potential": "DECIMAL(10, 2) DEFAULT 0",
        "sentiment_score": "DECIMAL(3, 2) DEFAULT 0",
        "csat_rating": "INTEGER DEFAULT 5"
    }
}

def migrate():
    # Try different paths for DB
    possible_paths = [
        "backend/resort_genius.db",
        "resort_genius.db",
        "../backend/resort_genius.db"
    ]
    
    db_path = None
    for p in possible_paths:
        if os.path.exists(p):
            db_path = p
            break
            
    if not db_path:
        # If not found, maybe create it in backend?
        # But we want to modify EXISTING.
        print(f"DB not found in: {possible_paths}")
        # Fallback to backend/resort_genius.db if we are at root
        if os.path.exists("backend"):
            db_path = "backend/resort_genius.db"
        else:
            return

    print(f"Migrating DB at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for table, columns in SCHEMA_CHANGES.items():
        # Check if table exists
        try:
            cursor.execute(f"SELECT 1 FROM {table} LIMIT 1")
        except sqlite3.OperationalError:
            print(f"Table {table} does not exist. Skipping (create_all should handle it).")
            continue
            
        # Get existing columns
        cursor.execute(f"PRAGMA table_info({table})")
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        for col, col_type in columns.items():
            if col not in existing_cols:
                try:
                    print(f"Adding {col} to {table}...")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
                except Exception as e:
                    print(f"Failed to add {col} to {table}: {e}")
            else:
                pass # print(f"{col} exists in {table}")
                
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
