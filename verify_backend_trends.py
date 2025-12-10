import sys
import os
from datetime import datetime, timedelta

# Add request to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.metrics_service import MetricsService
from app.database import SessionLocal, engine, Base
from app.models import Query

# FORCE DB PATH to backend/resort_genius.db
import os
db_path = os.path.join(os.getcwd(), 'backend', 'resort_genius.db')
if os.path.exists(db_path):
    print(f"Found DB at: {db_path}")
    # We need to hack the engine or just chdir
    os.chdir('backend')
else:
    print(f"DB not found at {db_path}. CWD: {os.getcwd()}")

def verify_trends():
    service = MetricsService()
    
    # Inspect Raw Query
    session = SessionLocal()
    first = session.query(Query).first()
    if first:
        print(f"First Query ID: {first.id}")
        print(f"Timestamp: {first.timestamp} (Type: {type(first.timestamp)})")
        # Check if strftime works via SQL
        try:
            from sqlalchemy import func
            sql_time = session.query(func.strftime('%Y-%m-%d %H:00:00', Query.timestamp)).first()
            print(f"SQL strftime result: {sql_time}")
        except Exception as e:
            print(f"SQL Error: {e}")
    else:
        print("No queries in DB at all.")
    session.close()

    # Test 7 days (168h)
    print("--- Testing 7 Days (168h) ---")
    trends = service.get_hourly_trends(hours=168)
    print(f"Count: {len(trends)}")
    if trends:
        print(f"Sample: {trends[0]}")
        print(f"Last: {trends[-1]}")
    else:
        print("No trends found.")

    # Test Custom Range (Last 30 days)
    print("\n--- Testing Custom Range (30 Days) ---")
    end = datetime.utcnow()
    start = end - timedelta(days=30)
    trends_custom = service.get_hourly_trends(hours=0, start_date=start, end_date=end)
    print(f"Count: {len(trends_custom)}")
    if trends_custom:
         print(f"Sample: {trends_custom[0]}")
    
if __name__ == "__main__":
    verify_trends()
