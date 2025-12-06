
import sys
import os
# Add parent dir to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.services.auth_service import AuthService
    # Generate hash for "demo"
    print(AuthService.hash_password("demo"))
except Exception as e:
    print(f"Error: {e}")
