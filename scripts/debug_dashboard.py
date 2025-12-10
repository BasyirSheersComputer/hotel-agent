
import os
import sys

# 1. Setup Path to allow 'from app import ...'
backend_path = os.path.join(os.getcwd(), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

# 2. Force correct DB path for SQLAlchemy BEFORE importing app.database
db_path = os.path.abspath(os.path.join(os.getcwd(), 'backend', 'resort_genius.db'))
# Use forward slashes for safer SQLite URL on Windows
db_url = f"sqlite:///{db_path.replace(os.sep, '/')}"
os.environ["DATABASE_URL"] = db_url

print(f"Setting DATABASE_URL to: {db_url}")

# 3. Import app modules
try:
    from app.services.metrics_service import get_metrics_service
    from app.database import SessionLocal
    from app.models import User
except ImportError as e:
    print(f"Import Error: {e}")
    print("sys.path is:", sys.path)
    sys.exit(1)

def debug_metrics():
    org_id = "f0e43d9c-d6b7-439a-afb6-33a9ddf4208e"
    print(f"Testing Metrics for Org: {org_id}")
    
    try:
        service = get_metrics_service()
        print("Calling get_summary_metrics...")
        data = service.get_summary_metrics(hours=24, org_id=org_id)
        if data:
            print("Success! Data keys:", data.keys())
            print(data)
        else:
            print("Returned Empty Data!")
            
    except Exception as e:
        print("FAILED!")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_metrics()
