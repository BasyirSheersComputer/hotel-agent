import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models import Query
from app.config.settings import DEMO_ORG_ID
from datetime import datetime, timedelta
import uuid

db = SessionLocal()
try:
    print("Seeding 1 dummy transaction...")
    q = Query(
        query_text="I want to book the Presidential Suite and order champagne.",
        response_time_ms=1200,
        question_category="Booking",
        source_type="RAG",
        agent_id="agent-007",
        org_id=uuid.UUID(DEMO_ORG_ID), # Demo Org
        success=True,
        tokens_used=500,
        cost_estimate=0.015,
        accuracy_score=0.98,
        aht_saved_s=300,
        
        # Financials
        booking_intent=True,
        upsell_intent=True,
        revenue_potential=2500.00, # Suite + Champagne
        sentiment_score=0.9,
        csat_rating=5,
        is_sop_compliant=True,
        correct_on_first_try=True
    )
    db.add(q)
    db.commit()
    print("Seeding complete.")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
