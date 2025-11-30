import requests
import json

# Test the new FAQ questions
questions = [
    "Do you have a fridge or minibar in the room?",
    "What toiletries are provided?",
    "Is there a pantry in the room?",
    "Do you provide coffee and tea?",
    "Do you have a room for 4 people?",
    "What is the maximum occupancy per room?",
    "Do you have special rates for 1 week or 1 month stays?",
    "Do you have washing machine or laundry services?",
    "When is peak season and off-peak season?",
    "Which month is best to visit?",
    "How many parking spaces per unit?"
]

url = "http://localhost:8000/api/chat"
results = []

print("Testing 11 new FAQ questions...")
print("=" * 80)

for i, question in enumerate(questions, 1):
    print(f"\n[{i}/11] Testing: {question}")
    data = {"query": question}
    response = requests.post(url, json=data)
    result = response.json()
    
    answer = result.get('answer', 'No answer')
    sources = result.get('sources', [])
    
    # Check if comprehensive_knowledge.txt is cited
    has_correct_source = any('comprehensive_knowledge.txt' in str(s) for s in sources)
    
    results.append({
        'question': question,
        'answer_preview': answer[:150] + "..." if len(answer) > 150 else answer,
        'correct_source': '✅' if has_correct_source else '❌'
    })
    
    print(f"  Answer preview: {answer[:100]}...")
    print(f"  Source check: {results[-1]['correct_source']}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
correct_sources = sum(1 for r in results if r['correct_source'] == '✅')
print(f"Questions answered from comprehensive_knowledge.txt: {correct_sources}/11")
print("=" * 80)

# Save detailed results
with open("faq_test_results.txt", "w", encoding="utf-8") as f:
    f.write("FAQ QUESTION TEST RESULTS\n")
    f.write("=" * 80 + "\n\n")
    for i, r in enumerate(results, 1):
        f.write(f"Q{i}: {r['question']}\n")
        f.write(f"Answer: {r['answer_preview']}\n")
        f.write(f"Source: {r['correct_source']}\n")
        f.write("-" * 80 + "\n\n")
    f.write(f"\nTotal: {correct_sources}/11 from correct source\n")

print("\nDetailed results saved to: faq_test_results.txt")
