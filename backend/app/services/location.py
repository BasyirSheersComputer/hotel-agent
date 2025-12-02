"""
Copyright (c) 2025 Sheers Software Sdn. Bhd.
All Rights Reserved.

Location-based service for finding nearby amenities using Google Maps Places API.
This service is used when users ask about "nearest X" where X is an external attraction/amenity.
"""

import os
import math
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Club Med Cherating coordinates
HOTEL_LAT = 4.1383924
HOTEL_LNG = 103.4079572
HOTEL_NAME = "Club Med Cherating"

# Google Maps API configuration
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.
    Returns distance in kilometers.
    """
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def search_nearby_places(
    place_type: str,
    radius: int = 5000,
    max_results: int = 5
) -> List[Dict]:
    """
    Search for nearby places of a specific type using Google Places Nearby Search API.
    
    Args:
        place_type: Type of place to search for (e.g., 'hospital', 'atm', 'restaurant')
        radius: Search radius in meters (default: 5000m = 5km)
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        List of dictionaries containing place information with calculated distances
    """
    if not GOOGLE_MAPS_API_KEY:
        return [{
            "error": "Google Maps API key not configured",
            "message": "Please set GOOGLE_MAPS_API_KEY environment variable"
        }]
    
    # Prepare API request
    params = {
        "location": f"{HOTEL_LAT},{HOTEL_LNG}",
        "radius": radius,
        "type": place_type,
        "key": GOOGLE_MAPS_API_KEY
    }
    
    try:
        response = requests.get(PLACES_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK":
            return [{
                "error": f"API returned status: {data.get('status')}",
                "message": data.get("error_message", "Unknown error")
            }]
        
        results = []
        places = data.get("results", [])[:max_results]
        
        for place in places:
            location = place.get("geometry", {}).get("location", {})
            place_lat = location.get("lat")
            place_lng = location.get("lng")
            
            # Calculate distance from hotel
            distance_km = haversine_distance(HOTEL_LAT, HOTEL_LNG, place_lat, place_lng)
            
            results.append({
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "distance_km": round(distance_km, 2),
                "distance_text": f"{round(distance_km, 2)} km" if distance_km >= 1 else f"{round(distance_km * 1000)} m",
                "rating": place.get("rating"),
                "open_now": place.get("opening_hours", {}).get("open_now"),
                "latitude": place_lat,
                "longitude": place_lng
            })
        
        # Sort by distance
        results.sort(key=lambda x: x["distance_km"])
        
        return results
    
    except requests.exceptions.RequestException as e:
        return [{
            "error": "API request failed",
            "message": str(e)
        }]


def format_nearby_results(places: List[Dict], place_type: str) -> str:
    """
    Format the nearby search results into a readable response.
    """
    if not places:
        return f"No {place_type}s found within the search radius."
    
    if places[0].get("error"):
        return f"Unable to search for nearby {place_type}s: {places[0].get('message', 'Unknown error')}"
    
    response = f"### Nearest {place_type.replace('_', ' ').title()}s from {HOTEL_NAME}\n\n"
    
    for i, place in enumerate(places, 1):
        response += f"**{i}. {place['name']}**\n"
        response += f"- Distance: {place['distance_text']}\n"
        response += f"- Address: {place['address']}\n"
        
        if place.get('rating'):
            response += f"- Rating: {place['rating']}/5.0\n"
        
        if place.get('open_now') is not None:
            status = "Open now" if place['open_now'] else "Closed now"
            response += f"- Status: {status}\n"
        
        response += "\n"
    
    return response


# Common place type mappings
PLACE_TYPE_MAPPINGS = {
    "hospital": "hospital",
    "clinic": "doctor",
    "doctor": "doctor",  # Added: singular doctor
    "doctors": "doctor",  # Added: plural doctors
    "medical": "hospital",
    "pharmacy": "pharmacy",
    "pharmacies": "pharmacy",  # Added: plural
    "drugstore": "pharmacy",
    "atm": "atm",
    "cash": "atm",
    "bank": "bank",
    "restaurant": "restaurant",
    "restaurants": "restaurant",  # Added: plural
    "food": "restaurant",
    "cafe": "cafe",
    "coffee": "cafe",
    "mall": "shopping_mall",
    "shopping": "shopping_mall",
    "supermarket": "supermarket",
    "grocery": "supermarket",
    "groceries": "supermarket",  # Added: plural groceries
    "convenience": "convenience_store",  # Added: convenience stores
    "convenience store": "convenience_store",  # Added: full phrase
    "shop": "store",  # Added: generic shop
    "shops": "store",  # Added: plural shops
    "store": "store",  # Added: generic store
    "stores": "store",  # Added: plural stores
    "gas station": "gas_station",
    "fuel": "gas_station",  # Added: fuel
    "fuel station": "gas_station",  # Added: fuel station
    "car": "gas_station",  # Added: for "fill up my car" type queries
    "petrol": "gas_station",
    "hotel": "lodging",
    "accommodation": "lodging",
    "mosque": "mosque",
    "church": "church",
    "temple": "hindu_temple",
    "tourist": "tourist_attraction",
    "attraction": "tourist_attraction",
    "museum": "museum",
    "park": "park",
    "beach": "natural_feature"
}


def get_place_type(query: str) -> Optional[str]:
    """
    Extract place type from user query.
    Returns the Google Places API type or None if not found.
    """
    query_lower = query.lower()
    
    for keyword, api_type in PLACE_TYPE_MAPPINGS.items():
        if keyword in query_lower:
            return api_type
    
    return None
