import requests

# Test the improved hierarchical formatting
url = "http://localhost:8000/api/chat"

questions = [
    "What are the restaurant operating hours?",
    "Tell me about the Kids Clubs",
    "What's included in the all-inclusive package?"
]

print("Testing improved main point / sub-point formatting...")
print("=" * 80)

for i, question in enumerate(questions, 1):
    print(f"\n[Test {i}/3] Question: {question}")
    print("-" * 80)
    
    data = {"query": question}
    response = requests.post(url, json=data)
    result = response.json()
    
    answer = result.get('answer', 'No answer')
    print("\nResponse:")
    print(answer)
    print("\n" + "=" * 80)

print("\n✓ Responses should now show:")
print("  - Clear headings (###)")
print("  - Main points with bullets (•)")
print("  - Sub-points properly indented")
print("  - Better visual hierarchy")
print("\nView formatted output at: http://localhost:3000")
