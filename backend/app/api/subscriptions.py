from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import datetime
from app.database import get_db
from app.api.auth import get_current_user
from app.models import User, Organization
from app.services.billing import BillingService
from app.core.context import get_tenant_id

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])
webhook_router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

class CheckoutRequest(BaseModel):
    plan_id: str # pro, enterprise
    success_url: str
    cancel_url: str

class PortalRequest(BaseModel):
    return_url: str

@router.post("/checkout")
async def create_checkout_session(
    request: CheckoutRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe Checkout Session for subscription upgrade.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can manage billing")
        
    org = db.query(Organization).filter(Organization.org_id == current_user.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    try:
        url = BillingService.get_checkout_url(
            org_id=str(org.org_id),
            plan_id=request.plan_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portal")
async def create_portal_session(
    request: PortalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create Customer Portal URL.
    """
    org = db.query(Organization).filter(Organization.org_id == current_user.org_id).first()
    if not org or not org.stripe_customer_id:
         # If no stripe ID, maybe they are on free plan or Mock mode?
         # In mock mode, just redirect back
         pass
         
    try:
        url = BillingService.get_portal_url(
            stripe_customer_id=org.stripe_customer_id or "mock_cust_id",
            return_url=request.return_url
        )
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@webhook_router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """
    Handle Stripe Webhooks (checkout.session.completed, etc)
    """
    payload = await request.body()
    try:
        event = BillingService.handle_webhook(payload, stripe_signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # Process Event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        org_id = session.get("client_reference_id")
        customer_id = session.get("customer")
        
        # Metadata
        plan = session.get("metadata", {}).get("plan", "pro")
        
        if org_id:
            org = db.query(Organization).filter(Organization.org_id == org_id).first()
            if org:
                # Update Org
                org.stripe_customer_id = customer_id
                org.subscription_status = "active"
                org.plan = plan
                # Extend limits based on plan?
                if plan == "pro":
                    org.max_users = 25
                    org.max_kb_docs = 500
                elif plan == "enterprise":
                    org.max_users = 999
                    org.max_kb_docs = 9999
                    
                db.commit()
                print(f"Billing: Upgraded Org {org.slug} to {plan}")
                
    return {"status": "success"}
