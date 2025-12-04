"""
Authentication service for multi-tenant SaaS.
Handles user registration, login, JWT token generation with org context.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import User, Organization
import uuid

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """
    Service for handling authentication operations.
    """
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storage."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """
        Create JWT access token with organization context.
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode and verify JWT token.
        Returns payload if valid, raises exception if invalid/expired.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str, org_slug: str) -> Optional[User]:
        """
        Authenticate a user by email, password, and organization slug.
        Returns User object if successful, None if failed.
        """
        # Find organization by slug
        org = db.query(Organization).filter(Organization.slug == org_slug).first()
        if not org:
            return None
        
        # Find user in that organization
        user = db.query(User).filter(
            User.email == email,
            User.org_id == org.org_id
        ).first()
        
        if not user:
            return None
        
        # Verify password
        if not AuthService.verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def create_user(
        db: Session,
        org_id: str,
        email: str,
        password: str,
        name: str,
        role: str = "agent"
    ) -> User:
        """
        Create a new user in an organization.
        """
        # Check if user already exists in this org
        existing = db.query(User).filter(
            User.email == email,
            User.org_id == org_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists in this organization"
            )
        
        # Create user
        user = User(
            user_id=uuid.uuid4(),
            org_id=org_id,
            email=email,
            password_hash=AuthService.hash_password(password),
            name=name,
            role=role
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def create_organization(
        db: Session,
        name: str,
        slug: str,
        admin_email: str,
        admin_password: str,
        admin_name: str
    ) -> tuple[Organization, User]:
        """
        Create a new organization with an admin user.
        Returns (Organization, Admin User).
        """
        # Check if slug already exists
        existing_org = db.query(Organization).filter(Organization.slug == slug).first()
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization with this slug already exists"
            )
        
        # Create organization
        org = Organization(
            org_id=uuid.uuid4(),
            name=name,
            slug=slug,
            plan="free"
        )
        db.add(org)
        db.flush()  # Get org_id without committing
        
        # Create admin user
        admin_user = AuthService.create_user(
            db=db,
            org_id=str(org.org_id),
            email=admin_email,
            password=admin_password,
            name=admin_name,
            role="admin"
        )
        
        db.commit()
        db.refresh(org)
        
        return org, admin_user
    
    @staticmethod
    def generate_token_for_user(user: User, org: Organization) -> dict:
        """
        Generate JWT token with user and org context.
        """
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={
                "sub": str(user.user_id),
                "user_id": str(user.user_id),
                "org_id": str(org.org_id),
                "org_slug": org.slug,
                "email": user.email,
                "role": user.role,
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": str(user.user_id),
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "org_slug": org.slug
            }
        }

# Global instance
_auth_service = None

def get_auth_service() -> AuthService:
    """Get or create the global auth service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
