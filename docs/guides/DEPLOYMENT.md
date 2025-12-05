# Deployment Instructions for Google Cloud

## Prerequisites

1. **Google Cloud Project Setup**
   - Ensure you have a Google Cloud project created
   - Enable Cloud Run API and Cloud Storage API
   - Install Google Cloud SDK (`gcloud` CLI)

2. **API Keys**
   - OPENAI_API_KEY (valid key from OpenAI)
   - GOOGLE_MAPS_API_KEY (valid key from Google Cloud Console)

## Step 1: Create GCS Bucket (One-time setup)

```bash
# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Create a bucket for the vector database
gsutil mb -l us-central1 gs://hotel-agent-vectordb

# Verify bucket was created
gsutil ls
```

## Step 2: Populate and Upload Vector Database

```bash
# 1. Ensure you have valid OpenAI API key in backend/.env
cd backend
cat .env  # Verify OPENAI_API_KEY is set

# 2. Populate the local vector database
python populate_db.py

# 3. Set GCS bucket name in environment
export GCS_BUCKET_NAME=hotel-agent-vectordb  # Windows: set GCS_BUCKET_NAME=hotel-agent-vectordb

# 4. Authenticate with Google Cloud (if not already)
gcloud auth application-default login

# 5. Upload database to GCS
cd ..
python upload_db_to_gcs.py
```

## Step 3: Deploy Backend to Cloud Run

```bash
# Navigate to backend directory
cd backend

# Deploy to Cloud Run (replace YOUR_PROJECT_ID)
gcloud run deploy hotel-agent-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="OPENAI_API_KEY=your-openai-key-here,GOOGLE_MAPS_API_KEY=your-maps-key-here,GCS_BUCKET_NAME=hotel-agent-vectordb"

# Note: Replace the API keys with your actual keys
```

## Step 4: Update Frontend with Backend URL

After deployment, Cloud Run will give you a URL like:
`https://hotel-agent-backend-HASH.run.app`

Update `frontend/script.js` line 3:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'
    : 'https://hotel-agent-backend-HASH.run.app';  // <-- Update this
```

## Step 5: Test Backend on Cloud

```bash
# Get the backend URL
gcloud run services describe hotel-agent-backend --region us-central1 --format="value(status.url)"

# Test health endpoint
curl https://hotel-agent-backend-HASH.run.app/health

# Test chat endpoint
curl -X POST https://hotel-agent-backend-HASH.run.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the restaurant operating hours?"}'
```

## Step 6: Deploy Frontend (Optional - Firebase Hosting)

If using Google Antigravity for frontend deployment:

```bash
cd frontend

# Follow Antigravity deployment prompts
# The tool will handle building and deploying the frontend
```

## Troubleshooting

### Backend not starting
- Check Cloud Run logs: `gcloud run services logs read hotel-agent-backend --region us-central1`
- Verify environment variables are set correctly
- Ensure GCS bucket exists and is accessible

### Vector DB not found
- Verify upload was successful: `gsutil ls gs://hotel-agent-vectordb/chroma_db_v2/`
- Check Cloud Run service account has Storage Object Viewer role

### API key errors
- Ensure OPENAI_API_KEY is valid and has credits
- Verify GOOGLE_MAPS_API_KEY has Places API enabled

## Cost Optimization

- Cloud Run: Pay only when requests are processed
- Cloud Storage: ~$0.02/GB/month for standard storage
- Consider setting up Cloud Run minimum instances to 0 for cost savings
