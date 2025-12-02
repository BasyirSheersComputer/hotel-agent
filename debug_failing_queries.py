import requests
import json

# Debug specific failing queries
url = "http://localhost:8000/api/chat"

failing_queries = [
    "Show me local doctors",
    "Any convenience stores nearby?",
    "Where can I buy groceries?",
    "Show me fuel stations nearby",
]

print("=" * 80)
print("DEBUGGING FAILING QUERIES")
print("=" * 80)

for query in failing_queries:
    print(f"\n{'=' * 80}")
    print(f"Query: {query}")
    print("=" * 80)
    
    try:
        response = requests.post(url, json={"query": query}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            sources = result.get('sources', [])
            answer = result.get('answer', '')
            
            # Determine source type
            if "Google Maps" in str(sources):
                source_type = "Google Maps (✓ CORRECT)"
            elif sources:
                source_type = "Knowledge Base (✗ WRONG - should be Maps)"
            else:
                source_type = "Unknown"
            
            print(f"Source: {source_type}")
            print(f"Sources list: {sources}")
            print(f"\nAnswer preview:")
            print(answer[:300])
            print("...")
            
        else:
            print(f"❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

print("\n" + "=" * 80)
