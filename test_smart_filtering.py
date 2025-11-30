import requests

# Test the improved filtering logic
url = "http://localhost:8000/api/chat"

test_queries = [
    # These should use RAG (resort facilities)
    ("Where is the nearest beach to the hotel?", "RAG"),
    ("Is there a restaurant nearby?", "RAG"),
    ("Where can I find the swimming pool?", "RAG"),
    ("What's the closest bar?", "RAG"),
    
    # These should use Google Maps (external amenities)
    ("Where is the nearest hospital?", "Google Maps"),
    ("Is there an ATM nearby?", "Google Maps"),
    ("Where's the closest pharmacy?", "Google Maps"),
]

print("=" * 80)
print("TESTING SMART FILTERING - RESORT vs EXTERNAL AMENITIES")
print("=" * 80)

for i, (question, expected_source) in enumerate(test_queries, 1):
    print(f"\n[Test {i}/{len(test_queries)}]")
    print(f"Query: {question}")
    print(f"Expected: {expected_source}")
    print("-" * 80)
    
    try:
        response = requests.post(url, json={"query": question}, timeout=30)
        if response.status_code == 200:
            result = response.json()
            sources = result.get('sources', [])
            answer_preview = result.get('answer', '')[:150]
            
            # Determine actual source
            if "Google Maps" in str(sources):
                actual_source = "Google Maps"
            else:
                actual_source = "RAG"
            
            # Check if correct
            if actual_source == expected_source:
                print(f"✅ CORRECT - Using {actual_source}")
            else:
                print(f"❌ WRONG - Expected {expected_source}, got {actual_source}")
            
            print(f"Answer preview: {answer_preview}...")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 80)

print("\n✓ Testing complete!")
print("Resort facilities should use RAG (knowledge base)")
print("External amenities should use Google Maps")
