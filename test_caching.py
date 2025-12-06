
import asyncio
import time
import requests
import json
import os
import sys

# Ensure backend path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Use endpoint directly if server running
API_URL = "http://127.0.0.1:8001/api/chat"

# We assume server is running (User state says Uvicorn is running).
# We also need to supply auth token if standard mode, or demo mode?
# User is running with `python -m uvicorn ...`
# Demo mode might be on? `DEMO_MODE=true` in `.env`?
# I'll check `.env` if I can. But for now I will try to hit the endpoint.
# If auth required, I'll need a token.
# Assuming Demo Mode allows it or I have a token.
# Actually, I can use the internal function `query_rag` if I import it, but environment variables might not be loaded if run as script.
# Better to hit the RUNNING API.

async def test_cache():
    query = {"query": "What time is check in?", "history": [], "language": "en"}
    headers = {} 
    
    # Try to get token if needed (skipped for now, assuming demo or dev env)

    print(f"Sending Query 1 (Cold)...")
    start = time.time()
    try:
        response = requests.post(API_URL, json=query)
        duration = time.time() - start
        print(f"Status: {response.status_code}")
        print(f"Duration: {duration:.4f}s")
        if response.status_code == 200:
            print("Response:", response.json().get("answer")[:50] + "...")
        else:
            print("Error:", response.text)
    except Exception as e:
        print(f"Request Failed: {e}")
        return

    print("\nSending Query 2 (Warm)...")
    start = time.time()
    try:
        response = requests.post(API_URL, json=query)
        duration = time.time() - start
        print(f"Status: {response.status_code}")
        print(f"Duration: {duration:.4f}s")
        if response.status_code == 200:
            print("Response:", response.json().get("answer")[:50] + "...")
        else:
            print("Error:", response.text)
            
        if duration < 1.0:
            print("\nSUCCESS: Cache Hit! (Duration < 1s)")
        else:
            print("\nWARNING: Duration is high. Cache miss or overhead?")
            
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_cache())
