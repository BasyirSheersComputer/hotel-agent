from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
import re

from app.database import get_db
from app.models import Organization, Property, BillingAccount, Subscription
from app.middleware.auth import get_current_user, CurrentUser, require_tenant_admin
from app.config.settings import DEMO_MODE

router = APIRouter(prefix="/api/properties", tags=["Properties"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_property(
    request: dict, # {name, type}
    current_user: CurrentUser = Depends(require_tenant_admin()),
    db: Session = Depends(get_db)
):
    """
    Create a new property.
    Enforces Plan Limits.
    """
    org = db.query(Organization).filter(Organization.org_id == current_user.org_id).first()
    
    # 1. Check Plan Limits
    current_count = db.query(Property).filter(Property.org_id == org.org_id).count()
    limit = 1 # Default free
    
    if org.billing_account_id:
        sub = db.query(Subscription).filter(
            Subscription.account_id == org.billing_account_id,
            Subscription.status == "active"
        ).first()
        if sub:
            if "pro" in sub.plan_id:
                limit = 3
            elif "enterprise" in sub.plan_id:
                limit = 999
    
    if current_count >= limit:
        raise HTTPException(
            status_code=403, 
            detail=f"Property limit reached ({current_count}/{limit}). Please upgrade your plan."
        )

    # 2. Create Property
    name = request.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Property name required")
        
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    # Append random string ensure uniqueness
    slug = f"{slug}-{uuid.uuid4().hex[:6]}"
    
    new_prop = Property(
        property_id=uuid.uuid4(),
        org_id=org.org_id,
        name=name,
        slug=slug,
        timezone="UTC"
    )
    db.add(new_prop)
    db.commit()
    
    
    return {
        "property_id": str(new_prop.property_id),
        "name": new_prop.name,
        "slug": new_prop.slug
    }

@router.get("/", response_model=list[dict])
async def list_properties(
    current_user: CurrentUser = Depends(require_tenant_admin()),
    db: Session = Depends(get_db)
):
    """
    List all properties for the organization.
    """
    properties = db.query(Property).filter(Property.org_id == current_user.org_id).all()
    
    return [
        {
            "property_id": str(p.property_id),
            "name": p.name,
            "slug": p.slug
        } for p in properties
    ]
