"""
Database seeding script for v2.0 multi-tenant architecture.
Creates initial demo organization and users for testing.
Run from project root or backend directory.
"""
import os
import sys
from pathlib import Path

# Add backend directory to path (parent of this script's directory)
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database import SessionLocal
from app.models import Organization, User
from app.services.auth_service import AuthService
import uuid

def seed_database():
    """
    Seed database with demo organization and users.
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
        print(f"✗ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Resort Genius v2.0 - Database Seeder")
    print("=" * 60)
    
    seed_database()
    
    print("\n" + "=" * 60)
    print("Seeding complete!")
    print("=" * 60)
