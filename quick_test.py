import requests
import json

# Quick test of the API key
url = "http://localhost:8000/api/chat"

print("=" * 80)
print("TESTING GOOGLE MAPS API WITH NEW KEY")
print("=" * 80)

# Test location query
question = "What's the nearest hospital from the hotel?"
print(f"\nQuery: {question}")
print("-" * 80)

try:
    response = requests.post(url, json={"query": question}, timeout=30)
    if response.status_code == 200:
        result = response.json()
        answer = result.get('answer', 'No answer')
        sources = result.get('sources', [])
        
        print(f"\nAnswer:\n{answer}\n")
        print(f"\nSources: {sources}")
        
        # Check status
        if "Google Maps" in str(sources):
            if "invalid" in answer.lower() or "error" in answer.lower():
                print("\n❌ API Key still invalid - backend may need restart")
                print("\nPlease restart backend server:")
                print("1. Stop the uvicorn process (Ctrl+C)")
                print("2. Run: py -m uvicorn app.main:app --reload --port 8000")
            elif "Nearest" in answer and any(char.isdigit() for char in answer):
                print("\n✅ SUCCESS! Google Maps API is working!")
                print("✅ Showing real nearby hospitals with distances!")
            else:
                print("\n⚠️ Response received but check format")
        else:
            print("\n⚠️ Not using Google Maps API")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
