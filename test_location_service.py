import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.location import search_nearby_places

print("Testing location service directly...")
print("=" * 80)

results = search_nearby_places("hospital", radius=10000, max_results=3)

print(f"Results: {len(results)} items")
print("\n")

for i, result in enumerate(results, 1):
    print(f"{i}. {result}")
    print()

if results and results[0].get("error"):
    print(f"\n❌ ERROR DETECTED:")
    print(f"Error: {results[0].get('error')}")
    print(f"Message: {results[0].get('message')}")
else:
    print(f"\n✅ SUCCESS - Location service working!")
