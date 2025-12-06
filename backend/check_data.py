
from sqlalchemy import create_engine, text
import sys

SQLITE_DB_PATH = "./resort_genius.db"

def check():
    engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}")
    with engine.connect() as conn:
        print("Checking Organizations...")
        orgs = conn.execute(text("SELECT org_id, name FROM organizations")).fetchall()
        print(f"Orgs found: {len(orgs)}")
        for o in orgs:
            print(f" - {o.org_id}: {o.name}")

        print("\nChecking Users...")
        users = conn.execute(text("SELECT user_id, org_id FROM users")).fetchall()
        print(f"Users found: {len(users)}")
        
        print("\nChecking ChatSessions...")
        sessions = conn.execute(text("SELECT session_id, org_id FROM chat_sessions")).fetchall()
        print(f"Sessions found: {len(sessions)}")
        
        # Check integrity
        org_ids = [o.org_id for o in orgs]
        for s in sessions:
            if s.org_id not in org_ids:
                print(f"PROB: Session {s.session_id} has missing Org {s.org_id}")

if __name__ == "__main__":
    check()
