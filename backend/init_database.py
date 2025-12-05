"""
Database initialization script for v2.0 multi-tenant architecture.
Creates tables and initial demo organization for testing.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, Base, SessionLocal
from app.models import Organization, User
from app.services.auth_service import AuthService
import uuid

def init_database():
    """
    Initialize database with tables.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")

def create_demo_org():
    """
    Create a demo organization with admin user for testing.
    """
    db = SessionLocal()
    
    try:
        # Check if demo org already exists
        existing = db.query(Organization).filter(Organization.slug == "demo-hotel").first()
        if existing:
            print("ℹ Demo organization already exists")
            return
        
        print("\nCreating demo organization...")
        
        # Create demo organization
        demo_org = Organization(
            org_id=uuid.uuid4(),
            name="Demo Hotel",
            slug="demo-hotel",
            plan="pro"
        )
        db.add(demo_org)
        db.flush()
        
        # Create admin user
        admin_user = User(
            user_id=uuid.uuid4(),
            org_id=demo_org.org_id,
            email="admin@demo-hotel.com",
            password_hash=AuthService.hash_password("admin123"),
            name="Admin User",
            role="admin"
        )
        db.add(admin_user)
        
        # Create test agent user
        agent_user = User(
            user_id=uuid.uuid4(),
            org_id=demo_org.org_id,
            email="agent@demo-hotel.com",
            password_hash=AuthService.hash_password("agent123"),
            name="Test Agent",
            role="agent"
        )
        db.add(agent_user)
        
        db.commit()
        
        print("✓ Demo organization created:")
        print(f"  Organization: {demo_org.name} ({demo_org.slug})")
        print(f"  Admin: {admin_user.email} / admin123")
        print(f"  Agent: {agent_user.email} / agent123")
        
    except Exception as e:
        print(f"✗ Error creating demo org: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Resort Genius v2.0 - Database Initialization")
    print("=" * 60)
    
    # Check if using PostgreSQL or SQLite
    db_url = os.getenv("DATABASE_URL", "sqlite:///./resort_genius.db")
    print(f"\nDatabase: {db_url}")
    
    init_database()
    create_demo_org()
    
    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("=" * 60)
    print("\nYou can now test authentication:")
    print("  POST /api/auth/login")
    print("  {")
    print("    \"email\": \"admin@demo-hotel.com\",")
    print("    \"password\": \"admin123\",")
    print("    \"org_slug\": \"demo-hotel\"")
    print("  }")
