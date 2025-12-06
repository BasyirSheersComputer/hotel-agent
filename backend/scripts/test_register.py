
import urllib.request
import json
import ssl

url = "http://localhost:8001/api/auth/register"
data = {
    "email": "test_hash@example.com",
    "password": "demo",
    "name": "Hash Tester",
    "org_slug": "hash-test-resort"
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
