import requests
import json

print("="*80)
print("QUICK SYSTEM TEST")
print("="*80)

url = "http://localhost:8000/api/chat"

# Test queries
tests = [
    "What are the restaurant operating hours?",
    "Where is the nearest beach?",
    "Where is the nearest hospital?",
]

for i, query in enumerate(tests, 1):
    print(f"\n[Test {i}] Query: {query}")
    print("-" * 80)
    
    try:
        response = requests.post(url, json={"query": query}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'No answer')
            sources = result.get('sources', [])
            
            # Determine source type
            if "Google Maps" in str(sources):
                source_type = "Google Maps"
            elif sources:
                source_type = "Knowledge Base"
            else:
                source_type = "Unknown"
            
            # Show preview
            preview = answer[:200].replace('\n', ' ')
            print(f"✅ SUCCESS")
            print(f"Source: {source_type}")
            print(f"Preview: {preview}...")
            
            with open("test_results_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Test {i}: SUCCESS\nSource: {source_type}\nPreview: {preview}\n\n")
            
        else:
            print(f"❌ FAILED - HTTP {response.status_code}")
            print(f"Error: {response.text[:200]}")
            with open("test_results_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Test {i}: FAILED - {response.status_code}\nError: {response.text[:200]}\n\n")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        with open("test_results_log.txt", "a", encoding="utf-8") as f:
            f.write(f"Test {i}: EXCEPTION: {e}\n\n")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
