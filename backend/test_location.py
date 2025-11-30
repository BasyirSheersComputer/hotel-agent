"""
Test script for location-based amenities feature.
Tests Google Maps Places API integration for finding nearby attractions.
"""

import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.location import (
    search_nearby_places,
    format_nearby_results,
    get_place_type,
    HOTEL_LAT,
    HOTEL_LNG
)

print("=" * 80)
print("LOCATION-BASED AMENITIES FEATURE - TEST SUITE")
print("=" * 80)
print(f"\nClub Med Cherating Location: {HOTEL_LAT}, {HOTEL_LNG}")
print("\n" + "=" * 80)

# Test 1: Place type detection
print("\n[TEST 1] Place Type Detection")
print("-" * 80)
test_queries = [
    "What's the nearest hospital?",
    "Where is the closest ATM?",
    "Are there any restaurants nearby?",
    "Show me pharmacies in the area",
    "Is there a shopping mall close to the hotel?"
]

for query in test_queries:
    place_type = get_place_type(query)
    print(f"Query: '{query}'")
    print(f"  Detected type: {place_type}\n")

# Test 2: Nearby search (with mock/test)
print("\n" + "=" * 80)
print("[TEST 2] Nearby Search API")
print("-" * 80)
print("\nNOTE: This will make actual API calls if GOOGLE_MAPS_API_KEY is set.")
print("Searching for nearest hospitals within 10km radius...\n")

# Search for nearby hospitals
results = search_nearby_places("hospital", radius=10000, max_results=3)

if results and results[0].get("error"):
    print(f"⚠️ API Error: {results[0].get('message')}")
    print("\nTo enable this feature:")
    print("1. Get a Google Maps API key from: https://console.cloud.google.com/")
    print("2. Enable 'Places API' for your project")
    print("3. Add the key to backend/.env file:")
    print("   GOOGLE_MAPS_API_KEY=your_actual_api_key_here")
else:
    print(f"✓ Found {len(results)} results:")
    for place in results:
        print(f"\n  • {place['name']}")
        print(f"    Distance: {place['distance_text']}")
        print(f"    Address: {place['address']}")

# Test 3: Formatted output
print("\n" + "=" * 80)
print("[TEST 3] Formatted Output")
print("-" * 80)

formatted = format_nearby_results(results, "hospital")
print("\n" + formatted)

print("=" * 80)
print("TEST SUITE COMPLETED")
print("=" * 80)
