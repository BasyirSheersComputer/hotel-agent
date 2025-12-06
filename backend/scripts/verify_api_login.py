
import urllib.request
import json
import ssl

url = "http://127.0.0.1:8001/api/auth/login"
data = {
    "email": "demo@resort-genius.com",
    "password": "demo",
    "org_slug": "demo-hotel"
}

print(f"Testing Login against: {url}")
print(f"Payload: {json.dumps(data, indent=2)}")

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        body = response.read().decode('utf-8')
        print("Response Body:")
        print(body)
        parsed = json.loads(body)
        if parsed.get("access_token"):
            print("SUCCESS: Token received.")
        else:
            print("FAILURE: No token.")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
