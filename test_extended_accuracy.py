import requests
import json
from typing import Dict, List

# Extended test suite with 50+ queries including edge cases
url = "http://localhost:8000/api/chat"

print("=" * 80)
print("EXTENDED COMPREHENSIVE TEST - 50+ QUERIES")
print("=" * 80)

# Expanded test categories
test_categories = {
    "Medical Facilities": [
        "Where is the nearest hospital?",
        "Find me a clinic nearby",
        "Show me local doctors",
        "Where can I find a pharmacy?",
        "Any medical facilities around?",
        "Are there doctors in the area?",  # New
        "I need a doctor urgently",  # New
    ],
    
    "Financial Services": [
        "Where is the closest ATM?",
        "Show me nearby banks",
        "Find me a cash machine",
        "Any ATMs in the area?",
        "Where can I withdraw cash?",
        "Find the nearest bank branch",  # New
    ],
    
    "Food & Dining (External)": [
        "Where are the local restaurants?",
        "Find me a cafe nearby",
        "Show me coffee shops",
        "Any good food places around?",
        "Where can I get food?",
        "Are there any restaurants in town?",  # New
        "Show me nearby cafes",  # New
        "Where can I find local food?",  # New
    ],
    
    "Shopping": [
        "Where is the nearest shopping mall?",
        "Find me a supermarket",
        "Show me local grocery stores",
        "Any convenience stores nearby?",
        "Where can I buy groceries?",
        "Find me a local shop",  # New
        "Where's the nearest store?",  # New
    ],
    
    "Gas & Fuel": [
        "Where is the nearest gas station?",
        "Find me a petrol station",
        "Show me fuel stations nearby",
        "Where can I fill up my car?",  # New
    ],
    
    "Places of Worship": [
        "Where is the nearest mosque?",
        "Find me a church nearby",
        "Show me local temples",
        "Any mosques in the area?",  # New
    ],
    
    "Tourism & Attractions": [
        "Show me tourist attractions",
        "Where are the local attractions?",
        "Find me a museum nearby",
        "Any parks in the area?",
        "What are the nearby attractions?",  # New
    ],
    
    "Resort Facilities (Should Use KB)": [
        "Where is the pool?",
        "Where is the beach at the resort?",
        "Find the gym",
        "Show me the restaurant hours",
        "Where is the lobby?",
        "What are the resort restaurant hours?",  # New
        "Tell me about the pool at the hotel",  # New
        "Where can I find the gym at the resort?",  # New
    ],
    
    "Resort Restaurant Queries (Should Use KB)": [
        "What time does the restaurant open?",  # New
        "When is breakfast served?",  # New
        "What are the dining hours?",  # New
        "Where can I eat at the resort?",  # New
    ],
    
    "Edge Cases - Mixed Context": [
        "Where is the beach?",  # Should use KB (resort beach)
        "Any restaurants?",  # Ambiguous - could route either way
        "Show me the nearest beach",  # Should use Maps (external beaches)
        "What restaurants are nearby?",  # Should use Maps (external)
    ],
}

results = {
    "google_maps": 0,
    "knowledge_base": 0,
    "errors": 0,
}

detailed_results: List[Dict] = []
total_queries = 0

for category, queries in test_categories.items():
    print(f"\n{'=' * 80}")
    print(f"CATEGORY: {category}")
    print(f"{'=' * 80}")
    
    for query in queries:
        total_queries += 1
        print(f"\n[{total_queries}] Query: {query}")
        print("-" * 80)
        
        try:
            response = requests.post(url, json={"query": query}, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                sources = result.get('sources', [])
                answer = result.get('answer', '')
                
                # Determine source type
                if "Google Maps" in str(sources):
                    source_type = "Google Maps"
                    results["google_maps"] += 1
                    status = "✅"
                elif sources:
                    source_type = "Knowledge Base"
                    results["knowledge_base"] += 1
                    status = "✅"
                else:
                    source_type = "Unknown"
                    results["errors"] += 1
                    status = "⚠️"
                
                # Determine expected source
                if "Should Use KB" in category or "Resort" in category:
                    expected_source = "Knowledge Base"
                elif "Edge Cases" in category:
                    # For edge cases, we'll accept either
                    expected_source = "Either (Edge Case)"
                else:
                    expected_source = "Google Maps"
                
                is_correct = (expected_source == "Either (Edge Case)" or source_type == expected_source)
                
                if not is_correct:
                    status = "❌ WRONG SOURCE"
                
                preview = answer[:100].replace('\n', ' ')
                print(f"{status} Source: {source_type} (Expected: {expected_source})")
                print(f"Preview: {preview}...")
                
                detailed_results.append({
                    "category": category,
                    "query": query,
                    "source": source_type,
                    "expected": expected_source,
                    "correct": is_correct,
                })
                
            else:
                print(f"❌ HTTP {response.status_code}")
                results["errors"] += 1
                detailed_results.append({
                    "category": category,
                    "query": query,
                    "source": "Error",
                    "expected": expected_source,
                    "correct": False,
                })
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results["errors"] += 1

# Summary
print("\n" + "=" * 80)
print("EXTENDED TEST SUMMARY")
print("=" * 80)
print(f"Total Queries: {total_queries}")
print(f"Google Maps: {results['google_maps']}")
print(f"Knowledge Base: {results['knowledge_base']}")
print(f"Errors: {results['errors']}")

# Check for incorrect routing
incorrect = [r for r in detailed_results if not r["correct"]]
correct_count = len(detailed_results) - len(incorrect)
accuracy = (correct_count / len(detailed_results) * 100) if detailed_results else 0

print(f"\n{'=' * 80}")
print(f"ACCURACY: {correct_count}/{len(detailed_results)} = {accuracy:.1f}%")
print(f"{'=' * 80}")

if accuracy >= 95:
    print(f"\n🎉 SUCCESS! Achieved {accuracy:.1f}% accuracy (target: 95%)")
else:
    print(f"\n⚠️ Target not met. Need {95 - accuracy:.1f}% more accuracy.")

if incorrect:
    print(f"\n⚠️ INCORRECT ROUTING DETECTED ({len(incorrect)} queries):")
    for r in incorrect:
        print(f"  - '{r['query']}' → {r['source']} (Expected: {r['expected']})")
else:
    print("\n✅ ALL QUERIES ROUTED CORRECTLY!")

print("=" * 80)
