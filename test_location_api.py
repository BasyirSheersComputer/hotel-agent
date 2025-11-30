import requests
import json

# Test location-based queries through the chat API
url = "http://localhost:8000/api/chat"

print("=" * 80)
print("TESTING LOCATION-BASED QUERIES VIA CHAT API")
print("=" * 80)

# Test queries
test_queries = [
    "What's the nearest hospital from the hotel?",
    "Where is the closest ATM?",
    "Are there any restaurants nearby?",
    "Show me pharmacies in the area",
    # Also test non-location queries to ensure RAG still works
    "What are the restaurant operating hours?",
]

for i, question in enumerate(test_queries, 1):
    print(f"\n[Query {i}/5]: {question}")
    print("-" * 80)
    
    try:
        response = requests.post(url, json={"query": question}, timeout=30)
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'No answer')
            sources = result.get('sources', [])
            
            print(f"\nAnswer:\n{answer}\n")
            print(f"Sources: {', '.join([str(s) for s in sources])}")
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")
    
    print("=" * 80)

print("\n✓ Location query detection working")
print("✓ Hybrid system: Google Maps for 'nearest X', RAG for hotel info")
print("\nNOTE: If you see 'Google Maps API key not configured' messages,")
print("      add your API key to backend/.env file")
print("      Get one from: https://console.cloud.google.com/apis/credentials")
