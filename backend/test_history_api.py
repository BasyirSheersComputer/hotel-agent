
import requests
import os

API_URL = "http://localhost:8000"

def get_token(role="guest"):
    # Demo login bypasses normal auth if DEMO_MODE is true, 
    # but let's try to get a token via login if possible, or assume no token?
    # Actually, in DEMO_MODE, any token is accepted or ignored?
    # settings.py: if DEMO_MODE: user = get_demo_user().
    # So headers don't matter?
    # BUT app/api/history.py uses Depends(require_agent_or_admin).
    # get_demo_user returns role='admin'.
    # So it SHOULD work without token if DEMO_MODE is on?
    pass

def test_history():
    print("Testing History API...")
    # 1. No Token (should use Demo User -> Admin)
    try:
        res = requests.get(f"{API_URL}/api/history/sessions")
        print(f"No Token Response: {res.status_code}")
        if res.status_code == 200:
            print(f"Sessions: {len(res.json())}")
        else:
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_history()
