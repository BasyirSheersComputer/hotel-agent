import requests
import time
import json

BASE_URL = "http://localhost:8000/api"

def get_total_queries():
    try:
        resp = requests.get(f"{BASE_URL}/metrics/summary?hours=24")
        resp.raise_for_status()
        data = resp.json()
        return data.get("total_queries", 0)
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return None

def send_chat_query():
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": "demo-org" # Ensure tenant context
    }
    payload = {
        "query": "Is the spa open on Sundays?",
        "agent_id": "integration_tester",
        "language": "en"
    }
    
    # Try /chat/query first (common pattern)
    url = f"{BASE_URL}/chat/query" 
    print(f"Attempting POST to {url}")
    
    try:
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code == 404:
            # Try /chat
            url = f"{BASE_URL}/chat"
            print(f"404. Attempting POST to {url}")
            resp = requests.post(url, json=payload, headers=headers)
            
        print(f"Chat Response Code: {resp.status_code}")
        # print(f"Chat Response: {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error sending chat: {e}")
        return False

def main():
    print("--- Starting Integration Test ---")
    
    initial_count = get_total_queries()
    if initial_count is None:
        print("FAIL: Could not get initial metrics.")
        return

    print(f"Initial Query Count: {initial_count}")
    
    if send_chat_query():
        print("Chat query sent successfully. Waiting for background processing...")
        time.sleep(2) # Allow background tasks to process
        
        final_count = get_total_queries()
        print(f"Final Query Count: {final_count}")
        
        if final_count > initial_count:
            print("SUCCESS: Metrics updated correctly.")
        else:
            print("FAIL: Metrics did not increase.")
    else:
        print("FAIL: Chat query failed.")

if __name__ == "__main__":
    main()
