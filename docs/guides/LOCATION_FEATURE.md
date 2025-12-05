# Location-Based Amenities Feature Documentation

## Overview
The system now supports location-based queries for finding nearby attractions and amenities using Google Maps Places API.

## Features
- **Automatic Query Detection**: Detects "nearest", "nearby", "closest", etc.
- **Distance Calculation**: Uses Haversine formula for accurate distances
- **Place Type Mapping**: Supports 20+ amenity types (hospitals, ATMs, restaurants, pharmacies, etc.)
- **Hybrid System**: Google Maps for location queries, RAG for hotel information

## Implementation Details

### Files Created/Modified
1. **`backend/app/services/location.py`** (NEW)
   - Google Maps Places API integration
   - Haversine distance calculation
   - Place type detection and mapping
   - Result formatting

2. **`backend/app/services/retrieval.py`** (MODIFIED)
   - Added location query detection
   - Routes to Google Maps when "nearest X" detected
   - Falls back to RAG for hotel-specific questions

3. **`backend/.env`** (MODIFIED)
   - Added `GOOGLE_MAPS_API_KEY` configuration

### Hotel Coordinates
- **Club Med Cherating**: 4.1383924°N, 103.4079572°E
- **Search Radius**: 10km (configurable)
- **Max Results**: 5 places per query

### Supported Place Types
The system understands queries about:
- Medical: hospital, clinic, pharmacy, doctor
- Financial: ATM, bank, cash
- Food: restaurant, cafe, coffee, food
- Shopping: mall, supermarket, grocery
- Services: gas station, parking
- Religious: mosque, church, temple
- Tourism: tourist attractions, museum, park

### Example Queries
✓ "What's the nearest hospital?"
✓ "Where is the closest ATM?"
✓ "Are there any restaurants nearby?"
✓ "Show me pharmacies in the area"
✓ "Is there a shopping mall close to the hotel?"

### Response Format
```markdown
### Nearest Hospitals from Club Med Cherating

**1. Hospital Name**
- Distance: 5.2 km
- Address: Street Address
- Rating: 4.5/5.0
- Status: Open now

**2. Another Hospital**
- Distance: 7.8 km
- Address: Street Address  
- Rating: 4.2/5.0
```

## Setup Instructions

### For Development/Testing
1. Get a Google Maps API key:
   - Visit: https://console.cloud.google.com/apis/credentials
   - Create a new project or use existing
   - Enable "Places API"
   - Create API key

2. Add to `backend/.env`:
   ```
   GOOGLE_MAPS_API_KEY=your_actual_api_key_here
   ```

3. Restart backend server for changes to take effect

### API Key Not Required
- System works without API key
- Returns helpful error message: "Google Maps API key not configured"
- Instructs user how to set up API key
- Regular RAG queries (hotel info) work normally

## Testing
Run tests with:
```bash
# Test location service directly
cd backend
py test_location.py

# Test via chat API (end-to-end)
cd ..
py test_location_api.py
```

## Architecture

### Query Flow
1. User asks: "What's the nearest hospital?"
2. `retrieval.py` detects location keywords ("nearest")
3. `location.py` extracts place type ("hospital")
4. Google Maps API called with hotel coordinates
5. Results sorted by distance (Haversine formula)
6. Formatted response returned

### Hybrid Intelligence
- **Location queries** → Google Maps Places API
- **Hotel questions** → RAG (ChromaDB + GPT-4o)
- Seamless switching based on query type

## Limitations
- Requires internet connection for Google Maps API
- API has usage quotas (check Google Cloud Console)
- 10km search radius (can be adjusted)
- Maximum 5 results per query (configurable)

## Future Enhancements
- [ ] Cache frequently requested locations
- [ ] Add driving/walking time estimates
- [ ] Support custom radius in queries
- [ ] Multi-language support for place names
- [ ] Integration with hotel concierge recommendations
