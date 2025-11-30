import requests
import json

# Test with the updated Google Maps API key
url = "http://localhost:8000/api/chat"

print("=" * 80)
print("TESTING GOOGLE MAPS INTEGRATION WITH UPDATED API KEY")
print("=" * 80)

# Test location-based query
test_queries = [
    "What's the nearest hospital from the hotel?",
    "Where is the closest ATM?",
    "Are there any restaurants nearby?",
]

for i, question in enumerate(test_queries, 1):
    print(f"\n[Test {i}/{len(test_queries)}] Query: {question}")
    print("-" * 80)
    
    try:
        response = requests.post(url, json={"query": question}, timeout=30)
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'No answer')
            sources = result.get('sources', [])
            
            print(f"\nAnswer Preview:")
            # Show first 300 chars of answer
            preview = answer[:300] + "..." if len(answer) > 300 else answer
            print(preview)
            print(f"\nSources: {sources}")
            
            # Check if it's using Google Maps
            if "Google Maps" in str(sources):
                print("✅ Using Google Maps Places API")
            elif "API key not configured" in answer or "error" in answer.lower():
                print("❌ API key issue detected")
            else:
                print("ℹ️ Using RAG knowledge base (expected for non-location queries)")
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 80)

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("If you see '✅ Using Google Maps Places API', the integration is working!")
print("If you see '❌ API key issue', please check:")
print("  1. API key is correctly added to backend/.env")
print("  2. Places API is enabled in Google Cloud Console")
print("  3. Backend server was restarted after adding the key")
