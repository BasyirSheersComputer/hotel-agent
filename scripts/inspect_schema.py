
import sqlite3
import os

def inspect():
    db_path = os.path.join(os.getcwd(), 'backend', 'resort_genius.db')
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    print(f"Inspecting {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    table = "queries"
    print(f"--- Columns in {table} ---")
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        rows = cursor.fetchall()
        for r in rows:
            print(f"{r[1]} ({r[2]})")
            
        if not any(r[1] == 'sentiment_score' for r in rows):
            print("!!! MISSING sentiment_score !!!")
        else:
            print("OK: sentiment_score present.")
            
    except Exception as e:
        print(f"Error: {e}")
        
    conn.close()

if __name__ == "__main__":
    inspect()
