
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.auth_service import AuthService

pw = "demo"
print("Generating hash...")
h = AuthService.hash_password(pw)
print(f"Generated: {h}")
print(f"Verifying: {AuthService.verify_password(pw, h)}")
