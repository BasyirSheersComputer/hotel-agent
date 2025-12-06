import os
import sys
import asyncio
import time
import requests
from sqlalchemy import create_engine, text
from redis import Redis

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.env_utils import load_env_robustly
load_env_robustly()

from app.database import DATABASE_URL

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def check_postgres():
    print("Checking PostgreSQL connection...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"✅ Postgres Connection Successful! Result: {result.scalar()}")
            return True
    except Exception as e:
        print(f"❌ Postgres Connection Failed: {e}")
        return False

def check_redis():
    print("\nChecking Redis connection...")
    try:
        r = Redis.from_url(REDIS_URL, decode_responses=True)
        r.ping()
        print("✅ Redis Connection Successful!")
        return True
    except Exception as e:
        print(f"❌ Redis Connection Failed: {e}")
        return False

def check_google_maps():
    print("\nChecking Google Maps API...")
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("❌ GOOGLE_MAPS_API_KEY not found in environment.")
        return False
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": "4.1383924,103.4079572", # Club Med Cherating
        "radius": "1000",
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get('status') in ['OK', 'ZERO_RESULTS']:
            print("✅ Google Maps API is working!")
            return True
        else:
            print(f"❌ Google Maps API Error: {data.get('status')} - {data.get('error_message')}")
            return False
    except Exception as e:
        print(f"❌ Google Maps Request Failed: {e}")
        return False

def check_backend_api():
    print("\nChecking Backend API Health Endpoint...")
    url = "http://localhost:8000/health"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend API is Healthy! {response.json()}")
            return True
        else:
            print(f"❌ Backend API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend API Request Failed: {e} (Is the server running?)")
        return False

if __name__ == "__main__":
    print("="*60)
    print("RESORT GENIUS SYSTEM HEALTH CHECK")
    print("="*60)
    
    results = {
        "Postgres": check_postgres(),
        "Redis": check_redis(),
        "GoogleMaps": check_google_maps(),
        "BackendAPI": check_backend_api()
    }
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    all_passed = True
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service}")
        if not status:
            all_passed = False
            
    if all_passed:
        print("\n🎉 ALL SYSTEMS GO!")
        sys.exit(0)
    else:
        print("\n⚠️ SOME SYSTEMS FAILED!")
        sys.exit(1)
