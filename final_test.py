import requests
import json

# Test multiple questions
questions = [
    "What are the restaurant operating hours?",
    "Tell me about the Kids Clubs - what ages and costs?",
   "Do you allow pets and smoking?",
    "Is parking free?",
    "What's included in the all-inclusive package?"
]

url = "http://localhost:8000/api/chat"
all_outputs = []

for question in questions:
    data = {"query": question}
    response = requests.post(url, json=data)
    result = response.json()
    
    all_outputs.append("=" * 80)
    all_outputs.append(f"QUERY: {question}")
    all_outputs.append("=" * 80)
    all_outputs.append(f"ANSWER: {result.get('answer', 'No answer')}")
    all_outputs.append("=" * 80)
    all_outputs.append("SOURCES:")
    for source in result.get("sources", []):
        all_outputs.append(f"- {source}")
    all_outputs.append("=" * 80)
    all_outputs.append("")

# Write to file
with open("final_test_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(all_outputs))

print(f"Tested {len(questions)} questions - results saved to final_test_results.txt")
