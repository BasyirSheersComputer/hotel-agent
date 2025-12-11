"""
SaaS Configuration Settings.
Feature flags to toggle between demo mode and full SaaS.
"""
import os
from typing import Optional
import uuid

print("DEBUG: Loading settings.py...")

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# =============================================================================
# DEMO MODE CONFIGURATION

# =============================================================================
# When DEMO_MODE is True:
# - Authentication is bypassed (all requests treated as demo user)
# - Single tenant (demo org) is used
# - Rate limiting is disabled
# - CORS allows all origins
#
# When DEMO_MODE is False:
# - Full JWT authentication required
# - Multi-tenant isolation enforced
# - Rate limiting active per plan
# - CORS restricted to whitelisted origins
# =============================================================================

DEMO_MODE = True # Force enabled for demo-v1
print(f"DEBUG: SETTINGS_PY LOADED. DEMO_MODE={DEMO_MODE}")

# Demo tenant and user (used when DEMO_MODE=true)
DEMO_ORG_ID = os.getenv("DEMO_ORG_ID", "00000000-0000-0000-0000-000000000001")
DEMO_ORG_SLUG = os.getenv("DEMO_ORG_SLUG", "demo-hotel")
DEMO_USER_ID = os.getenv("DEMO_USER_ID", "00000000-0000-0000-0000-000000000001")
DEMO_USER_EMAIL = os.getenv("DEMO_USER_EMAIL", "demo@resort-genius.com")
DEMO_USER_ROLE = "admin"

# =============================================================================
# JWT CONFIGURATION
# =============================================================================
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# =============================================================================
# RATE LIMITING CONFIGURATION
# =============================================================================
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true" and not DEMO_MODE

# Rate limits by plan (requests per minute)
RATE_LIMITS = {
    "free": 20,
    "pro": 100,
    "enterprise": 1000,
}

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
# In demo mode, allow all origins. In SaaS mode, restrict to whitelisted origins.
CORS_ALLOW_ALL = DEMO_MODE or os.getenv("CORS_ALLOW_ALL", "false").lower() == "true"

CORS_ALLOWED_ORIGINS = [
    origin.strip() 
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,https://resort-genius.com").split(",")
    if origin.strip()
]

# =============================================================================
# FEATURE FLAGS
# =============================================================================
ENABLE_DASHBOARD = os.getenv("ENABLE_DASHBOARD", "true").lower() == "true"
ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
ENABLE_MULTI_LANGUAGE = os.getenv("ENABLE_MULTI_LANGUAGE", "false").lower() == "true"

# =============================================================================
# PLAN LIMITS
# =============================================================================
PLAN_LIMITS = {
    "free": {
        "max_users": 3,
        "max_kb_docs": 50,
        "max_queries_per_day": 100,
    },
    "pro": {
        "max_users": 25,
        "max_kb_docs": 500,
        "max_queries_per_day": 5000,
    },
    "enterprise": {
        "max_users": -1,  # Unlimited
        "max_kb_docs": -1,
        "max_queries_per_day": -1,
    },
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def get_current_mode() -> str:
    """Return current operating mode for logging/debugging."""
    return "DEMO" if DEMO_MODE else "SAAS"

def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled."""
    features = {
        "dashboard": ENABLE_DASHBOARD,
        "analytics": ENABLE_ANALYTICS,
        "multi_language": ENABLE_MULTI_LANGUAGE,
    }
    return features.get(feature, False)
