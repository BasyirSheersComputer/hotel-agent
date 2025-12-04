"""
Rate Limiting Middleware.
Per-tenant rate limiting based on subscription plan.
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Tuple

from app.config.settings import DEMO_MODE, RATE_LIMIT_ENABLED, RATE_LIMITS


class RateLimiter:
    """
    Simple in-memory rate limiter.
    For production, should use Redis for distributed rate limiting.
    """
    
    def __init__(self):
        # {key: [(timestamp, count), ...]}
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, key: str, limit: int, window_seconds: int = 60) -> Tuple[bool, int]:
        """
        Check if request is allowed under rate limit.
        
        Returns:
            (is_allowed, remaining_requests)
        """
        async with self._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window_seconds)
            
            # Clean old entries
            self._requests[key] = [
                ts for ts in self._requests[key]
                if ts > window_start
            ]
            
            current_count = len(self._requests[key])
            
            if current_count >= limit:
                return False, 0
            
            self._requests[key].append(now)
            return True, limit - current_count - 1
    
    def clear(self, key: str = None):
        """Clear rate limit data for a key or all keys."""
        if key:
            self._requests.pop(key, None)
        else:
            self._requests.clear()


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    
    In DEMO_MODE or when RATE_LIMIT_ENABLED=false: No rate limiting.
    In SAAS_MODE: Applies per-tenant rate limits based on plan.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting in demo mode or when disabled
        if DEMO_MODE or not RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get tenant info
        org_id = getattr(request.state, 'org_id', None)
        plan = getattr(request.state, 'plan', 'free') if hasattr(request.state, 'current_user') else 'free'
        
        # Determine rate limit key
        if org_id:
            key = f"org:{org_id}"
        else:
            # Fall back to IP-based limiting for unauthenticated requests
            client_ip = request.client.host if request.client else "unknown"
            key = f"ip:{client_ip}"
            plan = "free"  # Unauthenticated gets free tier limits
        
        # Get limit for plan
        limit = RATE_LIMITS.get(plan, RATE_LIMITS["free"])
        
        # Check rate limit
        allowed, remaining = await rate_limiter.is_allowed(key, limit)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": limit,
                    "window": "60 seconds",
                    "retry_after": 60
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60"
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
