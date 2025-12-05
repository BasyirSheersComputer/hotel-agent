# Google Maps API Troubleshooting Guide

## Issue: "The provided API key is invalid"

Your API key: `AIzaSyDAuqDqh8T7zrf_oo8OgKqefpHDuM4y1n8`

### ✅ What's Working
- Backend server restarted successfully
- New API key loaded from .env
- Location query detection working
- API integration code working

### ❌ What's Failing
Google Maps API is rejecting the API key

### 🔧 How to Fix

Follow these steps **in order**:

#### Step 1: Enable Places API
1. Visit: https://console.cloud.google.com/apis/library/places-backend.googleapis.com
2. Make sure you're in the correct project
3. Click the blue **"ENABLE"** button
4. Wait for confirmation

#### Step 2: Configure API Key Restrictions
1. Visit: https://console.cloud.google.com/apis/credentials
2. Find and click on your API key: `AIzaSyDAuqDqh8T7zrf_oo8OgKqefpHDuM4y1n8`
3. Scroll to **"API restrictions"**
4. Select **"Restrict key"** (not "Don't restrict key")
5. In the dropdown, find and check **"Places API"**
6. Click **"Save"** at the bottom
7. Wait 1-2 minutes for changes to propagate

#### Step 3: Verify Billing
1. Visit: https://console.cloud.google.com/billing
2. Ensure billing is enabled for your project
3. Add payment method if needed
   - New accounts get **$300 free credit**
   - Places API is very cheap (first $200/month free)

#### Step 4: Test Again
Once you've completed steps 1-3:
1. Wait 1-2 minutes for Google's systems to update
2. Go to: http://localhost:3000
3. Ask: "What's the nearest hospital from the hotel?"
4. You should see actual hospital names with distances!

### 🎯 Expected Result
When working, you'll see responses like:
```
### Nearest Hospitals from Club Med Cherating

**1. Hospital Name**
- Distance: 5.2 km
- Address: Street Address
- Rating: 4.5/5.0
- Status: Open now
```

### ⚠️ Still Not Working?
If you've done all 3 steps and it's still not working:
1. Try creating a **completely new API key**
2. Make sure you're using the same Google Cloud project
3. Check the browser's network tab for the exact error message

Let me know which step resolved your issue!
