
import os
import sys

# Ensure we can import app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Force DB
db_path = os.path.abspath(os.path.join(os.getcwd(), 'backend', 'resort_genius.db'))
db_url = f"sqlite:///{db_path.replace(os.sep, '/')}"
os.environ["DATABASE_URL"] = db_url

from app.database import SessionLocal
from app.models import User
from app.services.auth_service import AuthService

def reset_password(email, new_password):
    print(f"Resetting password for {email}...")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} not found!")
            return
            
        hashed = AuthService.hash_password(new_password)
        user.password_hash = hashed
        db.commit()
        print(f"Success! Password for {email} set to: {new_password}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: py reset_password.py <email> <password>")
    else:
        reset_password(sys.argv[1], sys.argv[2])
