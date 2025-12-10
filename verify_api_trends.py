import requests
import json

BASE_URL = "http://localhost:8000"
LOGIN_payload = {
    "email": "admin@demo-hotel.com",
    "password": "admin123",
    "org_slug": "demo-hotel"
}

def verify_api():
    session = requests.Session()
    
    # 1. Login
    print(f"Logging in to {BASE_URL}/api/auth/login...")
    try:
        resp = session.post(f"{BASE_URL}/api/auth/login", json=LOGIN_payload)
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login success.")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 2. Test 7 Days (168h)
    print("\n--- Testing API 7 Days (168h) ---")
    try:
        resp = session.get(f"{BASE_URL}/api/metrics/trends?hours=168", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Count: {len(data)}")
            if data:
                print(f"First: {data[0]}")
                print(f"Last: {data[-1]}")
            else:
                print("Response is empty list []")
        else:
            print(f"Request failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. Test 30 Days (720h)
    print("\n--- Testing API 30 Days (720h) ---")
    try:
        resp = session.get(f"{BASE_URL}/api/metrics/trends?hours=720", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Count: {len(data)}")
            if data:
                print(f"First: {data[0]}")
        else:
            print(f"Request failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_api()
