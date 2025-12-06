"""
Copyright (c) 2025 Sheers Software Sdn. Bhd.
All Rights Reserved.

Resort Genius API - Main Application
Multi-tenant SaaS with demo mode support.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.env_utils import load_env_robustly

# Load environment variables before importing other modules
load_env_robustly()

# Import configuration
from app.config.settings import (
    DEMO_MODE, CORS_ALLOW_ALL, CORS_ALLOWED_ORIGINS,
    ENABLE_DASHBOARD, get_current_mode
)

# Import routers
from app.api import chat, dashboard, admin, history
from app.api.auth import router as auth_router

# Import middleware
from app.middleware.tenant import TenantContextMiddleware
from app.middleware.ratelimit import RateLimitMiddleware

# Validate environment variables
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY not found. Chat functionality will fail.")
if not os.getenv("GOOGLE_MAPS_API_KEY"):
    print("WARNING: GOOGLE_MAPS_API_KEY not found. Location services will fail.")

# Create FastAPI app
app = FastAPI(
    title="Resort Genius API",
    description="Multi-tenant AI concierge for hotels and resorts",
    version="2.0.0",
    docs_url="/docs" if DEMO_MODE else None,  # Disable docs in production
    redoc_url="/redoc" if DEMO_MODE else None,
)

# =============================================================================
# MIDDLEWARE STACK (order matters - first added = outermost)
# =============================================================================

# 1. CORS - must be first
if CORS_ALLOW_ALL:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Tenant-ID"],
    )

# 2. Tenant Context - sets org_id in request state
app.add_middleware(TenantContextMiddleware)

# 3. Rate Limiting - demo mode bypassed
app.add_middleware(RateLimitMiddleware)

# =============================================================================
# ROUTERS
# =============================================================================

# Auth endpoints (login, register, etc.)
app.include_router(auth_router, prefix="/api")

# Chat endpoints
app.include_router(chat.router, prefix="/api")

# Dashboard endpoints (feature-flagged)
if ENABLE_DASHBOARD:
    app.include_router(dashboard.router, prefix="/api")

# Admin endpoints (KB management, requires admin role)
app.include_router(admin.router)

# History endpoints
app.include_router(history.router)

# =============================================================================
# ROOT ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint with system info."""
    return {
        "service": "Resort Genius API",
        "version": "2.0.0",
        "mode": get_current_mode(),
        "demo_mode": DEMO_MODE,
        "features": {
            "dashboard": ENABLE_DASHBOARD,
            "auth_required": not DEMO_MODE,
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "mode": get_current_mode()}


# =============================================================================
# STARTUP
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    print(f"=" * 60)
    print(f"Resort Genius API Starting")
    print(f"Mode: {get_current_mode()}")
    print(f"Demo Mode: {DEMO_MODE}")
    print(f"Dashboard: {'Enabled' if ENABLE_DASHBOARD else 'Disabled'}")
    print(f"CORS: {'Allow All' if CORS_ALLOW_ALL else 'Restricted'}")
    print(f"=" * 60)
