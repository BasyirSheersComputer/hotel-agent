
import os
import sys
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import Base
from app.models import Organization, Property, User, ChatSession

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_multi_property_logic():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        # 1. Create Organization (Tenant)
        print("Creating Organization: Club Med...")
        org = Organization(name="Club Med", slug="club-med")
        db.add(org)
        db.commit()
        db.refresh(org)
        print(f"Org Created: {org.org_id}")
        
        # 2. Create Properties
        print("Creating Properties: Cherating and Borneo...")
        prop_a = Property(org_id=org.org_id, name="Club Med Cherating", slug="cm-cherating")
        prop_b = Property(org_id=org.org_id, name="Club Med Borneo", slug="cm-borneo")
        db.add_all([prop_a, prop_b])
        db.commit()
        db.refresh(prop_a)
        db.refresh(prop_b)
        print(f"Property A: {prop_a.property_id} ({prop_a.name})")
        print(f"Property B: {prop_b.property_id} ({prop_b.name})")
        
        # 3. Create Users (Scoped to Property)
        print("Creating Users...")
        user_cherating = User(
            org_id=org.org_id,
            property_id=prop_a.property_id,
            email="manager@cherating.com",
            password_hash="hashed",
            name="Cherating Manager",
            role="property_manager"
        )
        
        user_hq = User(
            org_id=org.org_id,
            property_id=None, # access to all
            email="admin@clubmed.com",
            password_hash="hashed",
            name="HQ Admin",
            role="tenant_admin"
        )
        
        db.add_all([user_cherating, user_hq])
        db.commit()
        
        # 4. Create Data (Chat Sessions)
        print("Creating Chat Sessions...")
        # Session in Cherating
        session_a = ChatSession(
            org_id=org.org_id,
            property_id=prop_a.property_id,
            user_id=user_cherating.user_id,
            title="Pool hours interaction"
        )
        db.add(session_a)
        db.commit()
        
        # 5. Verification Queries
        print("Verifying Scoping...")
        
        # Query: Find all properties for Org
        props = db.query(Property).filter(Property.org_id == org.org_id).all()
        assert len(props) == 2, f"Expected 2 properties, found {len(props)}"
        print("PASS: Org has correct properties")
        
        # Query: Find sessions for Cherating
        sessions_a = db.query(ChatSession).filter(ChatSession.property_id == prop_a.property_id).all()
        assert len(sessions_a) == 1, f"Expected 1 session for Cherating, found {len(sessions_a)}"
        print(f"PASS: Cherating has {len(sessions_a)} session")
        
        # Query: Find sessions for Borneo (Should be 0)
        sessions_b = db.query(ChatSession).filter(ChatSession.property_id == prop_b.property_id).all()
        assert len(sessions_b) == 0, f"Expected 0 sessions for Borneo, found {len(sessions_b)}"
        print(f"PASS: Borneo has {len(sessions_b)} sessions")
        
        print("\n=== MULTI-PROPERTY VERIFICATION SUCCESSFUL ===")
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_multi_property_logic()
