import sqlite3
import random
from datetime import datetime, timedelta
import os

# Database path
DB_PATH = "analytics.db"

def populate_data():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing data for a clean test
    cursor.execute("DELETE FROM queries")
    cursor.execute("DELETE FROM agents")
    print("Cleared existing data.")

    categories = ["Room Service", "Housekeeping", "Concierge", "Spa", "Dining", "Transport"]
    agents = ["Agent_Alpha", "Agent_Beta", "Agent_Gamma", "AI_Bot"]
    sources = ["RAG", "Maps", "General"]

    # Generate data for the last 24 hours
    now = datetime.now()
    start_time = now - timedelta(hours=24)
    
    total_queries = 150
    print(f"Generating {total_queries} dummy queries...")

    for _ in range(total_queries):
        # Random timestamp within the last 24 hours
        time_offset = random.randint(0, 24 * 60 * 60)
        timestamp = start_time + timedelta(seconds=time_offset)
        
        category = random.choice(categories)
        agent = random.choice(agents)
        source = random.choice(sources)
        success = random.random() > 0.1 # 90% success rate
        response_time = random.randint(500, 5000) # 0.5s to 5s
        tokens = random.randint(100, 1000)
        cost = (tokens / 1000) * 0.03
        accuracy = random.uniform(0.8, 1.0) if success else 0.0
        aht_saved = max(0, 300 - (response_time / 1000)) if success else 0

        cursor.execute("""
            INSERT INTO queries 
            (timestamp, query_text, response_time_ms, question_category, source_type, agent_id, success, tokens_used, cost_estimate, accuracy_score, aht_saved_s)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            f"Dummy query about {category}",
            response_time,
            category,
            source,
            agent,
            success,
            tokens,
            cost,
            accuracy,
            int(aht_saved)
        ))

        # Update agent stats
        cursor.execute("""
            INSERT INTO agents (agent_id, total_queries, last_seen)
            VALUES (?, 1, ?)
            ON CONFLICT(agent_id) DO UPDATE SET
                total_queries = total_queries + 1,
                last_seen = ?
        """, (agent, timestamp, timestamp))

    conn.commit()
    conn.close()
    print("Database populated successfully.")

if __name__ == "__main__":
    populate_data()
