import sys
import os
import uuid

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.auth_service import get_auth_service
from app.database import SessionLocal, engine, Base
from app.models import Organization, User

def verify_auth_service():
    print("="*50)
    print("VERIFYING AUTH SERVICE")
    print("="*50)
    
    db = SessionLocal()
    auth_service = get_auth_service()
    
    try:
        # 1. Create Organization
        org_slug = f"test-org-{uuid.uuid4().hex[:8]}"
        admin_email = f"admin-{uuid.uuid4().hex[:8]}@example.com"
        admin_password = "securepassword123"
        admin_name = "Admin User"
        
        print(f"1. Creating Organization '{org_slug}'...")
        org, admin = auth_service.create_organization(
            db=db,
            name="Test Org",
            slug=org_slug,
            admin_email=admin_email,
            admin_password=admin_password,
            admin_name=admin_name
        )
        print(f"   ✅ Organization created: {org.org_id}")
        print(f"   ✅ Admin user created: {admin.user_id}")
        
        # 2. Login (Authenticate)
        print(f"2. Authenticating as {admin_email}...")
        user = auth_service.authenticate_user(
            db=db,
            email=admin_email,
            password=admin_password,
            org_slug=org_slug
        )
        
        if user:
            print(f"   ✅ Authentication successful for user: {user.name}")
        else:
            print("   ❌ Authentication FAILED")
            return
            
        # 3. Generate Token
        print("3. Generating JWT Token...")
        token_data = auth_service.generate_token_for_user(user, org)
        access_token = token_data["access_token"]
        print(f"   ✅ Token generated: {access_token[:20]}...")
        
        # 4. Verify Token
        print("4. Verifying Token...")
        payload = auth_service.decode_token(access_token)
        if payload["sub"] == str(user.user_id) and payload["org_slug"] == org_slug:
             print(f"   ✅ Token verified successfully. User ID matches.")
        else:
             print(f"   ❌ Token verification failed. Payload: {payload}")

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("="*50)

if __name__ == "__main__":
    # Ensure tables exist (for SQLite)
    Base.metadata.create_all(bind=engine)
    verify_auth_service()
