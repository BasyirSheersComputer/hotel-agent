
import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import SessionLocal
from app.models import User

def check_role(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} NOT FOUND.")
        else:
            print(f"User: {email}")
            print(f"ID: {user.user_id}")
            print(f"Role: {user.role}")
            print(f"Org ID: {user.org_id}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Force DB Path
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'resort_genius.db'))
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    
    import logging
    logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
    
    email = sys.argv[1] if len(sys.argv) > 1 else "super@admin.com"
    check_role(email)
