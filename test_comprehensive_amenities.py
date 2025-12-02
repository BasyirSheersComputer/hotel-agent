import requests
import json
from typing import Dict, List

# Comprehensive test for all amenity types
url = "http://localhost:8000/api/chat"

print("=" * 80)
print("COMPREHENSIVE AMENITY QUERY TEST")
print("Testing all place types from PLACE_TYPE_MAPPINGS")
print("=" * 80)

# Test categories based on PLACE_TYPE_MAPPINGS
test_categories = {
    "Medical Facilities": [
        "Where is the nearest hospital?",
        "Find me a clinic nearby",
        "Show me local doctors",
        "Where can I find a pharmacy?",
        "Any medical facilities around?",
    ],
    
    "Financial Services": [
        "Where is the closest ATM?",
        "Show me nearby banks",
        "Find me a cash machine",
        "Any ATMs in the area?",
        "Where can I withdraw cash?",
    ],
    
    "Food & Dining": [
        "Where are the local restaurants?",
        "Find me a cafe nearby",
        "Show me coffee shops",
        "Any good food places around?",
        "Where can I get food?",
    ],
    
    "Shopping": [
        "Where is the nearest shopping mall?",
        "Find me a supermarket",
        "Show me local grocery stores",
        "Any convenience stores nearby?",
        "Where can I buy groceries?",
    ],
    
    "Gas & Fuel": [
        "Where is the nearest gas station?",
        "Find me a petrol station",
        "Show me fuel stations nearby",
    ],
    
    "Places of Worship": [
        "Where is the nearest mosque?",
        "Find me a church nearby",
        "Show me local temples",
    ],
    
    "Tourism & Attractions": [
        "Show me tourist attractions",
        "Where are the local attractions?",
        "Find me a museum nearby",
        "Any parks in the area?",
    ],
    
    "Resort Facilities (Should Use Knowledge Base)": [
        "Where is the pool?",
        "Where is the beach at the resort?",
        "Find the gym",
        "Show me the restaurant hours",
        "Where is the lobby?",
    ],
}

results = {
    "google_maps": 0,
    "knowledge_base": 0,
    "errors": 0,
}

detailed_results: List[Dict] = []

for category, queries in test_categories.items():
    print(f"\n{'=' * 80}")
    print(f"CATEGORY: {category}")
    print(f"{'=' * 80}")
    
    for query in queries:
        print(f"\nQuery: {query}")
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
                
                # For resort facilities, KB is correct; for external, Maps is correct
                expected_source = "Knowledge Base" if "Resort Facilities" in category else "Google Maps"
                is_correct = source_type == expected_source
                
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
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results["errors"] += 1

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total Queries: {sum(results.values())}")
print(f"Google Maps: {results['google_maps']}")
print(f"Knowledge Base: {results['knowledge_base']}")
print(f"Errors: {results['errors']}")

# Check for incorrect routing
incorrect = [r for r in detailed_results if not r["correct"]]
if incorrect:
    print(f"\n⚠️  INCORRECT ROUTING DETECTED ({len(incorrect)} queries):")
    for r in incorrect:
        print(f"  - '{r['query']}' → {r['source']} (Expected: {r['expected']})")
else:
    print("\n✅ ALL QUERIES ROUTED CORRECTLY!")

print("=" * 80)
