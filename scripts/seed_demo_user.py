import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.database import SessionLocal, engine, Base
from app.services.auth_service import get_auth_service, AuthService
from app.models import Organization, User

def seed_demo_user():
    print("="*50)
    print("SEEDING DEMO USER")
    print("="*50)
    
    db = SessionLocal()
    
    # Ensure tables exist
    print("0. Initializing Database Tables...")
    Base.metadata.create_all(bind=engine)
    
    auth_service = get_auth_service()
    
    try:
        org_slug = "demo-hotel"
        org_name = "Demo Hotel"
        admin_email = "admin@demo-hotel.com"
        admin_password = "password123"
        admin_name = "Admin User"
        
        # 1. Check/Create Organization
        print(f"1. Checking Organization '{org_slug}'...")
        org = db.query(Organization).filter(Organization.slug == org_slug).first()
        
        if not org:
            print(f"   Organization not found. Creating...")
            org, admin = auth_service.create_organization(
                db=db,
                name=org_name,
                slug=org_slug,
                admin_email=admin_email,
                admin_password=admin_password,
                admin_name=admin_name
            )
            print(f"   ✅ Organization created: {org.org_id}")
            print(f"   ✅ Admin user seeded: {admin.email} (Password: {admin_password})")
            return
        else:
            print(f"   Organization exists: {org.org_id}")

        # 2. Check/Reset User
        print(f"2. Checking User '{admin_email}'...")
        user = db.query(User).filter(
            User.email == admin_email,
            User.org_id == org.org_id
        ).first()
        
        if user:
            print(f"   User exists. Resetting password...")
            user.password_hash = AuthService.hash_password(admin_password)
            db.commit()
            print(f"   ✅ Password reset to: {admin_password}")
        else:
            print(f"   User not found. Creating...")
            user = auth_service.create_user(
                db=db,
                org_id=str(org.org_id),
                email=admin_email,
                password=admin_password,
                name=admin_name,
                role="admin"
            )
            print(f"   ✅ User created: {user.email} (Password: {admin_password})")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("="*50)

if __name__ == "__main__":
    seed_demo_user()
