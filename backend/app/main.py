"""
Copyright (c) 2025 Sheers Software Sdn. Bhd.
All Rights Reserved.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.env_utils import load_env_robustly

load_env_robustly()

from app.api import chat, dashboard

# Validate environment variables
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY not found in environment variables. Chat functionality will fail.")
if not os.getenv("GOOGLE_MAPS_API_KEY"):
    print("WARNING: GOOGLE_MAPS_API_KEY not found in environment variables. Location services will fail.")


app = FastAPI(title="Club Med Resort Genius API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP, allow all. In production, restrict to frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")

# Add dashboard router (feature-flagged)
ENABLE_DASHBOARD = os.getenv("ENABLE_DASHBOARD", "true").lower() == "true"
if ENABLE_DASHBOARD:
    app.include_router(dashboard.router, prefix="/api")
    print("✓ Dashboard API enabled")


@app.get("/")
async def root():
    return {"message": "Club Med Resort Genius API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
