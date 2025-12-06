import requests
import concurrent.futures
import time
import random
import json

BASE_URL = "http://localhost:8000/api"
AUTH_EMAIL = "demo@resort-genius.com"
AUTH_PASSWORD = "demo"
ORG_SLUG = "demo-hotel"

QUERIES = [
    "What are the restaurant hours?",
    "Where is the swimming pool?",
    "Do you have a gym?",
    "How do I connect to wifi?",
    "Is there a spa?",
    "Can I book a tennis court?",
    "What time is check out?",
    "Room service menu please",
    "Is there a kids club?",
    "Where is the nearest pharmacy?"
]

def login():
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": AUTH_EMAIL,
            "password": AUTH_PASSWORD,
            "org_slug": ORG_SLUG
        })
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def simulate_guest(user_id, token):
    print(f"User {user_id} starting session...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Simulate a session with 1-3 messages
    for i in range(random.randint(1, 3)):
        query = random.choice(QUERIES)
        print(f"User {user_id} sending: '{query}'")
        
        try:
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/chat", 
                headers=headers,
                json={"query": query}
            )
            duration = time.time() - start
            
            if response.status_code == 200:
                print(f"User {user_id} received response in {duration:.2f}s")
            else:
                print(f"User {user_id} error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"User {user_id} request failed: {e}")
            
        time.sleep(random.uniform(0.5, 2.0)) # Think time

    print(f"User {user_id} finished session.")

def run_simulation():
    print("Starting Data Audit Simulation...")
    print(f"Target: {BASE_URL}")
    
    token = login()
    if not token:
        print("Aborting: Could not authenticate.")
        return

    print("Authenticated successfully. Launching 100 concurrent guests...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(simulate_guest, i, token) for i in range(100)]
        concurrent.futures.wait(futures)
        
    print("Simulation complete.")

if __name__ == "__main__":
    run_simulation()
