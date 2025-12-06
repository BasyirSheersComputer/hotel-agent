
import requests
import time
import json

API_URL = "http://localhost:8000"

def get_baseline():
    print("Fetching baseline from gpt-4o (current)...")
    payload = {
        "query": "What are the check-in and check-out times?",
        "agent_id": "default",
        "session_id": "baseline-test"
    }
    
    start_time = time.time()
    try:
        res = requests.post(f"{API_URL}/api/chat", json=payload)
        duration = time.time() - start_time
        
        if res.status_code == 200:
            data = res.json()
            print(f"Status: {res.status_code}")
            print(f"Duration: {duration:.2f}s")
            print(f"Answer: {data['answer']}")
            return data['answer']
        else:
            print(f"Error: {res.status_code} - {res.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

if __name__ == "__main__":
    get_baseline()
