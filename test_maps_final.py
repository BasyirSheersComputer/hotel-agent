import requests
import json

# Test with saved output
url = "http://localhost:8000/api/chat"

test_queries = [
    "What's the nearest hospital from the hotel?",
    "Where is the closest ATM?",
]

output_lines = []
output_lines.append("=" * 80)
output_lines.append("GOOGLE MAPS API INTEGRATION TEST")
output_lines.append("=" * 80)

for i, question in enumerate(test_queries, 1):
    output_lines.append(f"\n[Test {i}] {question}")
    output_lines.append("-" * 80)
    
    try:
        response = requests.post(url, json={"query": question}, timeout=30)
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'No answer')
            sources = result.get('sources', [])
            
            output_lines.append(f"\nAnswer:\n{answer}\n")
            output_lines.append(f"Sources: {sources}")
            
            if "Google Maps" in str(sources):
                output_lines.append("✅ SUCCESS: Using Google Maps Places API")
            elif "API key not configured" in answer:
                output_lines.append("❌ FAILED: API key not loaded")
            else:
                output_lines.append("ℹ️ Using RAG (not a location query)")
        else:
            output_lines.append(f"❌ HTTP {response.status_code}: {response.text}")
    except Exception as e:
        output_lines.append(f"❌ Error: {e}")
    
    output_lines.append("=" * 80)

# Save to file
with open("maps_test_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

# Print to console
for line in output_lines:
    print(line)

print("\n✓ Results saved to: maps_test_results.txt")
