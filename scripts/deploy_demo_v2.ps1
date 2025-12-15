$ErrorActionPreference = "Stop"

Write-Host "Setting project to club-med-agent..."
gcloud config set project club-med-agent

Write-Host "Building Backend V2..."
gcloud builds submit backend --tag gcr.io/club-med-agent/hotel-backend-v2

Write-Host "Deploying Backend V2..."
# Deploy Backend to Cloud Run
$backendJson = gcloud run deploy hotel-backend-v2 `
    --image gcr.io/club-med-agent/hotel-backend-v2 `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars "OPENAI_API_KEY=sk-proj-fOt2fzfGJehntqqesYsjTpGY9CI-dBkXEsHadbEz7cYg8wIlurf2BmxdufP7AJiBqEsp3rqmJvANyFcYWNVqvgDUNbEzZK3cmBgAqcoq7CnLKonG-kPab5cMMqAJBZqBDvA,GCS_BUCKET_NAME=hotel-agent-vectordb,DEMO_MODE=true" `
    --port 8080 `
    --format="json" | ConvertFrom-Json

$backendUrl = $backendJson.status.url
Write-Host "Backend V2 deployed at: $backendUrl"

Write-Host "Building Frontend V2..."
gcloud builds submit frontend --config frontend/cloudbuild.yaml --substitutions="_NEXT_PUBLIC_API_URL=$backendUrl"

Write-Host "Deploying Frontend V2..."
$frontendJson = gcloud run deploy hotel-frontend-v2 `
    --image gcr.io/club-med-agent/hotel-frontend-v2 `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --set-env-vars "NEXT_PUBLIC_API_URL=$backendUrl" `
    --format="json" | ConvertFrom-Json

$frontendUrl = $frontendJson.status.url
Write-Host "Frontend V2 deployed at: $frontendUrl"

Write-Host "Deployment Complete."
Write-Host "Frontend URL: $frontendUrl"
