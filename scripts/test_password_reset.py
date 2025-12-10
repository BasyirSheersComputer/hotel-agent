
import requests
import sqlite3
import os
import sys

# Force DB path
db_path = os.path.abspath(os.path.join(os.getcwd(), 'backend', 'resort_genius.db'))
# No need for sqlalchemy here, just sqlite3
    
def test_flow():
    base_url = "http://localhost:8001" # Running on 8001 based on logs
    email = "test@test.com"
    new_pass = "newpass123"
    
    print(f"1. Requesting Forgot Password for {email}...")
    try:
        r = requests.post(f"{base_url}/api/auth/forgot-password", json={"email": email})
        print(f"Response: {r.status_code}, {r.json()}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to backend on 8001. Trying 8000...")
        base_url = "http://localhost:8000"
        r = requests.post(f"{base_url}/api/auth/forgot-password", json={"email": email})
        print(f"Response: {r.status_code}, {r.json()}")
        
    print(f"2. Fetching Token from DB at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT reset_token FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row[0]:
        print("FAILED: No reset token found in DB!")
        return
        
    token = row[0]
    print(f"Token found: {token}")
    
    print(f"3. Resetting Password...")
    r = requests.post(f"{base_url}/api/auth/reset-password", json={"token": token, "new_password": new_pass})
    print(f"Response: {r.status_code}, {r.json()}")
    
    if r.status_code != 200:
        print("FAILED to reset password")
        return
        
    print(f"4. Verifying Login with '{new_pass}'...")
    r = requests.post(f"{base_url}/api/auth/login", json={
        "email": email, 
        "password": new_pass, 
        "org_slug": "clubmed"
    })
    
    if r.status_code == 200:
        print("SUCCESS: Login verified!")
    else:
        print(f"FAILED: Login failed {r.status_code} {r.text}")

if __name__ == "__main__":
    test_flow()
