#!/bin/bash

# Hotel Agent - Google Cloud Deployment Script
# Project: club-med-agent
# Region: asia-southeast1

set -e  # Exit on error

PROJECT_ID="club-med-agent"
REGION="asia-southeast1"
GOOGLE_MAPS_API_KEY="AIzaSyC01CgQ_2qVB_jLFmM2HMrdY5Z8vq4aHWM"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Hotel Agent - Google Cloud Deployment ===${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI not found. Please install it first.${NC}"
    exit 1
fi

# Check if logged in
echo -e "${BLUE}Checking authentication...${NC}"
gcloud auth list --filter=status:ACTIVE --format="value(account)" > /dev/null 2>&1 || {
    echo -e "${RED}Not authenticated. Running gcloud auth login...${NC}"
    gcloud auth login
}

# Set project
echo -e "${BLUE}Setting project to ${PROJECT_ID}...${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "${BLUE}Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build and deploy backend
echo -e "${GREEN}Building backend...${NC}"
cd backend
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hotel-agent-backend

echo -e "${GREEN}Deploying backend to Cloud Run...${NC}"
gcloud run deploy hotel-agent-backend \
  --image gcr.io/${PROJECT_ID}/hotel-agent-backend \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY,GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY

# Get backend URL
BACKEND_URL=$(gcloud run services describe hotel-agent-backend --region=${REGION} --format='value(status.url)')
echo -e "${GREEN}Backend deployed at: ${BACKEND_URL}${NC}"

cd ..

# Update frontend script.js with backend URL
echo -e "${BLUE}Updating frontend API URL...${NC}"
sed -i.bak "s|http://localhost:8000|${BACKEND_URL}|g" frontend/script.js

# Build and deploy frontend
echo -e "${GREEN}Building frontend...${NC}"
cd frontend
gcloud builds submit --tag gcr.io/${PROJECT_ID}/hotel-agent-frontend

echo -e "${GREEN}Deploying frontend to Cloud Run...${NC}"
gcloud run deploy hotel-agent-frontend \
  --image gcr.io/${PROJECT_ID}/hotel-agent-frontend \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 256Mi \
  --cpu 1 \
  --port 80

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe hotel-agent-frontend --region=${REGION} --format='value(status.url)')

cd ..

# Restore original script.js
mv frontend/script.js.bak frontend/script.js

echo ""
echo -e "${GREEN}=== Deployment Complete! ===${NC}"
echo -e "${GREEN}Frontend URL: ${FRONTEND_URL}${NC}"
echo -e "${GREEN}Backend URL: ${BACKEND_URL}${NC}"
echo ""
echo -e "${BLUE}Test the deployment:${NC}"
echo "  curl ${BACKEND_URL}/health"
echo "  Open ${FRONTEND_URL} in your browser"
