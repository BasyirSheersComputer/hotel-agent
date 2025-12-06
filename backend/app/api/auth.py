"""
Authentication API Router.
Provides login, registration, and token management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models import User, Organization
from app.services.auth_service import AuthService
from app.config.settings import (
    DEMO_MODE, DEMO_ORG_ID, DEMO_USER_ID, DEMO_USER_EMAIL,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.middleware.auth import get_current_user, CurrentUser

router = APIRouter(prefix="/auth", tags=["Authentication"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    org_slug: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    org_slug: str  # Join existing org by slug


class CreateOrgRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    org_name: str  # Create new org


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user: dict


class UserResponse(BaseModel):
    user_id: str
    email: str
    name: Optional[str]
    role: str
    org_id: str
    org_slug: Optional[str]
    is_demo: bool


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    In DEMO_MODE: Returns demo token without validation.
    In SAAS_MODE: Validates credentials against database.
    """
    if DEMO_MODE:
        # Demo mode - return demo token
        token = AuthService.create_access_token(
            data={
                "sub": DEMO_USER_ID,
                "org_id": DEMO_ORG_ID,
                "email": DEMO_USER_EMAIL,
                "role": "admin"
            }
        )
        return TokenResponse(
            access_token=token,
            user={
                "user_id": DEMO_USER_ID,
                "email": DEMO_USER_EMAIL,
                "name": "Demo User",
                "role": "admin",
                "org_id": DEMO_ORG_ID,
                "org_slug": "demo-hotel",
                "is_demo": True
            }
        )
    
    print(f"Login Request: {request.email}, {request.org_slug}")
    # SaaS mode - validate credentials
    user = AuthService.authenticate_user(
        db, 
        request.email, 
        request.password, 
        request.org_slug
    )
    print(f"Auth Result: {user}")
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email, password, or organization",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Get organization
    org = db.query(Organization).filter(Organization.org_id == user.org_id).first()
    
    # Create token
    token = AuthService.create_access_token(
        data={
            "sub": str(user.user_id),
            "org_id": str(user.org_id),
            "email": user.email,
            "role": user.role
        }
    )
    
    return TokenResponse(
        access_token=token,
        user={
            "user_id": str(user.user_id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "org_id": str(user.org_id),
            "org_slug": org.slug if org else None,
            "is_demo": False
        }
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user in an existing organization.
    
    In DEMO_MODE: Returns demo token without creating user.
    In SAAS_MODE: Creates user in database.
    """
    if DEMO_MODE:
        # Demo mode - pretend to register
        token = AuthService.create_access_token(
            data={
                "sub": DEMO_USER_ID,
                "org_id": DEMO_ORG_ID,
                "email": request.email,
                "role": "agent"
            }
        )
        return TokenResponse(
            access_token=token,
            user={
                "user_id": DEMO_USER_ID,
                "email": request.email,
                "name": request.name,
                "role": "agent",
                "org_id": DEMO_ORG_ID,
                "org_slug": "demo-hotel",
                "is_demo": True
            }
        )
    
    # SaaS mode - create user
    # Find organization
    org = db.query(Organization).filter(Organization.slug == request.org_slug).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization '{request.org_slug}' not found"
        )
    
    # Check if email already exists in org
    existing = db.query(User).filter(
        User.email == request.email,
        User.org_id == org.org_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered in this organization"
        )
    
    # Create user
    user = User(
        user_id=uuid.uuid4(),
        org_id=org.org_id,
        email=request.email,
        password_hash=AuthService.hash_password(request.password),
        name=request.name,
        role="agent"  # Default role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create token
    token = AuthService.create_access_token(
        data={
            "sub": str(user.user_id),
            "org_id": str(user.org_id),
            "email": user.email,
            "role": user.role
        }
    )
    
    return TokenResponse(
        access_token=token,
        user={
            "user_id": str(user.user_id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "org_id": str(user.org_id),
            "org_slug": org.slug,
            "is_demo": False
        }
    )


@router.post("/create-org", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    request: CreateOrgRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new organization and register the first admin user.
    
    In DEMO_MODE: Returns demo token without creating org.
    In SAAS_MODE: Creates org and admin user in database.
    """
    if DEMO_MODE:
        # Demo mode - pretend to create org
        token = AuthService.create_access_token(
            data={
                "sub": DEMO_USER_ID,
                "org_id": DEMO_ORG_ID,
                "email": request.email,
                "role": "admin"
            }
        )
        return TokenResponse(
            access_token=token,
            user={
                "user_id": DEMO_USER_ID,
                "email": request.email,
                "name": request.name,
                "role": "admin",
                "org_id": DEMO_ORG_ID,
                "org_slug": "demo-hotel",
                "is_demo": True
            }
        )
    
    # SaaS mode - create organization and admin user
    import re
    
    # Generate slug from org name
    slug = re.sub(r'[^a-z0-9]+', '-', request.org_name.lower()).strip('-')
    
    # Check if slug already exists
    existing_org = db.query(Organization).filter(Organization.slug == slug).first()
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Organization '{slug}' already exists. Try a different name."
        )
    
    # Check if email already exists in any org
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered. Please login or use a different email."
        )
    
    # Create organization
    org = Organization(
        org_id=uuid.uuid4(),
        name=request.org_name,
        slug=slug,
        plan="free",  # Default to free plan
        max_users=10,
        max_kb_docs=100
    )
    db.add(org)
    db.flush()  # Get org_id without committing
    
    # Create admin user
    user = User(
        user_id=uuid.uuid4(),
        org_id=org.org_id,
        email=request.email,
        password_hash=AuthService.hash_password(request.password),
        name=request.name,
        role="admin"  # First user is always admin
    )
    db.add(user)
    
    # Commit both together
    db.commit()
    db.refresh(user)
    db.refresh(org)
    
    # Create token
    token = AuthService.create_access_token(
        data={
            "sub": str(user.user_id),
            "org_id": str(user.org_id),
            "email": user.email,
            "role": user.role
        }
    )
    
    return TokenResponse(
        access_token=token,
        user={
            "user_id": str(user.user_id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "org_id": str(user.org_id),
            "org_slug": org.slug,
            "is_demo": False
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get current authenticated user's information.
    """
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        org_id=current_user.org_id,
        org_slug=current_user.org_slug,
        is_demo=current_user.is_demo
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Refresh access token.
    """
    token = AuthService.create_access_token(
        data={
            "sub": current_user.user_id,
            "org_id": current_user.org_id,
            "email": current_user.email,
            "role": current_user.role
        }
    )
    
    return TokenResponse(
        access_token=token,
        user={
            "user_id": current_user.user_id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role,
            "org_id": current_user.org_id,
            "org_slug": current_user.org_slug,
            "is_demo": current_user.is_demo
        }
    )


@router.get("/status")
async def auth_status():
    """
    Return authentication system status.
    Useful for frontend to check if demo mode is active.
    """
    return {
        "demo_mode": DEMO_MODE,
        "auth_required": not DEMO_MODE,
        "message": "Demo mode active - authentication bypassed" if DEMO_MODE else "SaaS mode - authentication required"
    }
