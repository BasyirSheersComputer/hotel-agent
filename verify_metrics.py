import requests
import time
import os
from app.database import SessionLocal, engine, Base
from app.models import Query
from app.services.metrics_service import get_metrics_service
from sqlalchemy import func

def test_metrics():
    print(f"DB URL: {os.getenv('DATABASE_URL')}")
    
    # FORCE RECREATION OF TABLE
    print("--- Forcing Table Recreation ---")
    try:
        Query.__table__.drop(engine)
        print("Dropped queries table.")
    except Exception as e:
        print(f"Drop failed (might not exist): {e}")
        
    Query.__table__.create(engine)
    print("Created queries table from current model.")
    
    # Test 1: Direct Service Call
    print("--- Test 1: Direct Service Call ---")
    import uuid
    ms = get_metrics_service()
    fake_org_id = uuid.uuid4()
    try:
        qid = ms.log_query(
            query_text="Direct Test",
            response_time_ms=100,
            success=True,
            revenue_potential=999.0,
            hold_time_ms=50,
            booking_intent=True,
            org_id=str(fake_org_id)
        )
        print(f"Log Query returned ID: {qid}")
    except Exception as e:
        print(f"Direct Log Query FAILED: {e}")
        import traceback
        traceback.print_exc()

    # Verify DB
    session = SessionLocal()
    try:
        count = session.query(Query).count()
        revenue = session.query(func.sum(Query.revenue_potential)).scalar()
        print(f"Total Queries: {count}")
        print(f"Total Revenue: {revenue}")
        
        # Test Chat API
        print("--- Test 2: Chat API ---")
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={
                "query": "I want to book a suite",
                "agent_id": "test_script"
            }
        )
        print(f"Response Status: {response.status_code}")
        
    finally:
        session.close()

if __name__ == "__main__":
    test_metrics()
