import requests
import json

# Test enhanced location query detection
url = "http://localhost:8000/api/chat"

print("=" * 80)
print("TESTING ENHANCED LOCATION QUERY DETECTION")
print("=" * 80)

test_queries = [
    # Original issues
    "Where is the local pharmacy?",
    "Where can I find a pharmacy?",
    
    # Additional variations
    "Show me pharmacies",
    "Any ATMs around?",
    "Find me a hospital",
    "Where is the nearest bank?",
    
    # Should still use Knowledge Base (resort facilities)
    "Where is the pool?",
    "Where is the restaurant?",
]

for i, query in enumerate(test_queries, 1):
    print(f"\n[Test {i}] Query: {query}")
    print("-" * 80)
    
    try:
        response = requests.post(url, json={"query": query}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            sources = result.get('sources', [])
            answer = result.get('answer', 'No answer')
            
            # Determine source type
            if "Google Maps" in str(sources):
                source_type = "✓ Google Maps (External)"
            elif sources:
                source_type = "✓ Knowledge Base (Resort Info)"
            else:
                source_type = "? Unknown"
            
            # Show preview
            preview = answer[:150].replace('\n', ' ')
            print(f"Source: {source_type}")
            print(f"Preview: {preview}...")
            
        else:
            print(f"❌ FAILED - HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
