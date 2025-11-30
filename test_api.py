import requests
import json

# Test the API
url = "http://localhost:8000/api/chat"
data = {"query": "What are the restaurant operating hours?"}

response = requests.post(url, json=data)
result = response.json()

output = []
output.append("=" * 80)
output.append(f"QUERY: {data['query']}")
output.append("=" * 80)
output.append(f"ANSWER: {result.get('answer', 'No answer')}")
output.append("=" * 80)
output.append("SOURCES:")
for source in result.get("sources", []):
    output.append(f"- {source}")
output.append("=" * 80)

# Write to file
with open("test_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

# Also print to console
print("\n".join(output))
