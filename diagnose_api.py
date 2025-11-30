import requests

# Direct test of Google Maps API to get exact error
api_key = "AIzaSyDAuqDqh8T7zrf_oo8OgKqefpHDuM4y1n8"
url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

params = {
    "location": "4.1383924,103.4079572",  # Club Med Cherating
    "radius": "5000",
    "type": "hospital",
    "key": api_key
}

print("=" * 80)
print("DIRECT GOOGLE MAPS API TEST")
print("=" * 80)
print(f"\nAPI Key: {api_key}")
print(f"Endpoint: {url}")
print(f"\nTesting...\n")

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    print(f"HTTP Status: {response.status_code}")
    print(f"API Response Status: {data.get('status')}")
    
    if data.get('status') != 'OK':
        print(f"\n❌ ERROR: {data.get('status')}")
        print(f"Error Message: {data.get('error_message', 'No error message provided')}")
        
        # Provide specific troubleshooting
        if data.get('status') == 'REQUEST_DENIED':
            print("\n🔧 TROUBLESHOOTING for REQUEST_DENIED:")
            print("1. Check if Places API is enabled:")
            print("   → https://console.cloud.google.com/apis/library/places-backend.googleapis.com")
            print("\n2. Check API key restrictions:")
            print("   → https://console.cloud.google.com/apis/credentials")
            print("   → Click your API key")
            print("   → Under 'API restrictions': Select 'Restrict key'")
            print("   → Enable 'Places API' in the list")
            print("\n3. Check if billing is enabled:")
            print("   → https://console.cloud.google.com/billing")
            print("   → Must have valid payment method")
            
        elif data.get('status') == 'INVALID_REQUEST':
            print("\n🔧 TROUBLESHOOTING for INVALID_REQUEST:")
            print("Check the request parameters")
    else:
        print(f"\n✅ SUCCESS! Found {len(data.get('results', []))} places")
        print("\nFirst result:")
        if data.get('results'):
            place = data['results'][0]
            print(f"  Name: {place.get('name')}")
            print(f"  Address: {place.get('vicinity')}")
            
except Exception as e:
    print(f"❌ Request failed: {e}")

print("\n" + "=" * 80)
