
import sqlite3
import os
import sys

def check_db():
    # Force DB path for script usage
    db_path = os.path.join(os.getcwd(), 'backend', 'resort_genius.db')
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return
        
    print(f"Checking DB at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT email, role, org_id FROM users")
        users = cursor.fetchall()
        print(f"Users found: {len(users)}")
        for u in users:
            print(f"User: {u[0]}, Role: {u[1]}, OrgID: {u[2]}")

        cursor.execute("SELECT name, slug, org_id FROM organizations")
        orgs = cursor.fetchall()
        print(f"Orgs found: {len(orgs)}")
        for o in orgs:
            print(f"Org: {o[0]}, Slug: {o[1]}, ID: {o[2]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db()
