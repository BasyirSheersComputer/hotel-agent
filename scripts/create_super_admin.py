
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import SessionLocal
from app.models import User

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def make_super_admin(email: str):
    # Force DB Path to ensure we hit the Backend DB
    db_path = os.path.join(os.getcwd(), 'backend', 'resort_genius.db')
    if not os.path.exists(db_path):
        print(f"Warning: DB not found at {db_path}, trying default.")
        db = SessionLocal()
    else:
        print(f"Using DB at: {db_path}")
        engine = create_engine(f"sqlite:///{db_path}")
        SessionForce = sessionmaker(bind=engine)
        db = SessionForce()

    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} not found.")
            return
        
        user.role = "super_admin"
        db.commit()
        print(f"Successfully upgraded {email} to super_admin.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_super_admin.py <email>")
    else:
        make_super_admin(sys.argv[1])
