"""
Authentication Middleware and Dependencies.
Provides demo-aware authentication for FastAPI routes.
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from dataclasses import dataclass
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config.settings import (
    DEMO_MODE, DEMO_ORG_ID, DEMO_USER_ID, DEMO_USER_EMAIL, DEMO_USER_ROLE,
    JWT_SECRET_KEY, JWT_ALGORITHM
)
from app.database import get_db
from app.models import User, Organization

# HTTP Bearer token extractor
security = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    """
    Represents the currently authenticated user.
    In demo mode, returns demo user. In SaaS mode, returns actual user from JWT.
    """
    user_id: str
    org_id: str
    email: str
    role: str
    name: Optional[str] = None
    org_slug: Optional[str] = None
    plan: str = "free"
    is_demo: bool = False


def get_demo_user() -> CurrentUser:
    """Return demo user for demo mode."""
    return CurrentUser(
        user_id=DEMO_USER_ID,
        org_id=DEMO_ORG_ID,
        email=DEMO_USER_EMAIL,
        role=DEMO_USER_ROLE,
        name="Demo User",
        org_slug="demo-hotel",
        plan="enterprise",  # Demo gets full access
        is_demo=True
    )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> CurrentUser:
    """
    Get the current authenticated user.
    
    In DEMO_MODE: Returns demo user without authentication.
    In SAAS_MODE: Validates JWT and returns actual user.
    """
    # Demo mode bypass
    if DEMO_MODE:
        user = get_demo_user()
        request.state.current_user = user
        request.state.org_id = user.org_id
        return user
    
    # SaaS mode - require valid JWT
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        user_id: str = payload.get("sub")
        org_id: str = payload.get("org_id")
        
        if user_id is None or org_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        
        # Get user from database
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        # Get organization
        org = db.query(Organization).filter(Organization.org_id == org_id).first()
        
        current_user = CurrentUser(
            user_id=str(user.user_id),
            org_id=str(user.org_id),
            email=user.email,
            role=user.role,
            name=user.name,
            org_slug=org.slug if org else None,
            plan=org.plan if org else "free",
            is_demo=False
        )
        
        # Store in request state for middleware access
        request.state.current_user = current_user
        request.state.org_id = current_user.org_id
        
        return current_user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[CurrentUser]:
    """
    Optional authentication - returns None if not authenticated.
    Useful for endpoints that work with or without auth.
    """
    if DEMO_MODE:
        return get_demo_user()
    
    if not credentials:
        return None
    
    try:
        return await get_current_user(request, credentials, db)
    except HTTPException:
        return None


def require_role(allowed_roles: list[str]):
    """
    Dependency factory to require specific roles.
    
    Usage:
        @router.get("/admin", dependencies=[Depends(require_role(["admin"]))])
    """
    async def role_checker(user: CurrentUser = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' not authorized. Required: {allowed_roles}"
            )
        return user
    return role_checker


def require_super_admin():
    """Shorthand for requiring Super Admin role. (System Owner)"""
    return require_role(["super_admin"])

def require_tenant_admin():
    """Shorthand for requiring Tenant Admin role. (Org Owner)"""
    return require_role(["super_admin", "tenant_admin", "admin"]) # 'admin' for backward compat

def require_property_manager():
    """Shorthand for Property Manager."""
    return require_role(["super_admin", "tenant_admin", "admin", "property_manager"])

def require_admin():
    """Deprecated: Use require_tenant_admin. Kept for backward compat."""
    return require_tenant_admin()


def require_agent_or_admin():
    """Shorthand for requiring agent or higher."""
    return require_role(["super_admin", "tenant_admin", "admin", "property_manager", "agent"])
