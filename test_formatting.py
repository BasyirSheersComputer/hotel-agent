import requests

# Test the improved formatting
url = "http://localhost:8000/api/chat"

print("Testing improved formatting...")
print("=" * 80)

# Test question that should produce a well-formatted list
question = "What are the restaurant operating hours?"
data = {"query": question}

response = requests.post(url, json=data)
result = response.json()

print(f"Question: {question}")
print("\nAnswer (raw):")
print(result.get('answer', 'No answer'))
print("\n" + "=" * 80)
print("\nSources:")
for source in result.get('sources', []):
    print(f"  - {source}")

print("\n" + "=" * 80)
print("\n✓ Frontend should now display bullet points on separate lines")
print("✓ Bold text for restaurant names and times")
print("✓ Improved spacing and readability")
print("\nTest at: http://localhost:3000")
