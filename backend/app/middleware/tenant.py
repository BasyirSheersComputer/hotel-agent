"""
Tenant Context Middleware.
Injects tenant (organization) context into every request.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional

from app.config.settings import DEMO_MODE, DEMO_ORG_ID


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures every request has tenant context.
    
    In DEMO_MODE: Uses demo org ID.
    In SAAS_MODE: Extracts org_id from authenticated user (set by auth middleware).
    """
    
    async def dispatch(self, request: Request, call_next):
        # Initialize tenant context
        if DEMO_MODE:
            request.state.org_id = DEMO_ORG_ID
            request.state.is_demo = True
        else:
            # Will be set by auth middleware for protected routes
            # For unprotected routes, org_id remains None
            if not hasattr(request.state, 'org_id'):
                request.state.org_id = None
            request.state.is_demo = False
        
        # Set ContextVar for deep access (DB listeners)
        from app.core.context import set_tenant_id
        set_tenant_id(request.state.org_id)
        
        response = await call_next(request)
        return response


def get_tenant_id(request: Request) -> Optional[str]:
    """
    Helper to get current tenant ID from request.
    Returns None if no tenant context (unauthenticated public route).
    """
    return getattr(request.state, 'org_id', None)


def get_tenant_filter(org_id: Optional[str]):
    """
    Returns a SQLAlchemy filter condition for tenant isolation.
    
    Usage:
        query.filter(get_tenant_filter(request.state.org_id))
    """
    from app.models import ChatSession  # Import here to avoid circular
    
    if org_id is None:
        # No tenant context - return always-false filter
        return False
    
    return ChatSession.org_id == org_id
