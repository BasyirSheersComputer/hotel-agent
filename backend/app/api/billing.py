from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models import User, Organization, BillingAccount, Subscription, Property
from app.middleware.auth import get_current_user, CurrentUser, require_tenant_admin
from app.config.settings import DEMO_MODE

router = APIRouter(prefix="/api/billing", tags=["Billing"])

@router.post("/subscribe")
async def create_subscription(
    request: dict, # {email, name, plan_id, payment_method_id}
    db: Session = Depends(get_db)
):
    """
    Create a new Billing Account and Subscription.
    Used during Onboarding.
    """
    # Mock Stripe Integration
    account_id = uuid.uuid4()
    billing_account = BillingAccount(
        account_id=account_id,
        billing_email=request.get("email"),
        billing_name=request.get("name"),
        stripe_customer_id=f"cus_{uuid.uuid4().hex[:8]}", # Mock
        balance=0.00
    )
    db.add(billing_account)
    
    sub_id = uuid.uuid4()
    subscription = Subscription(
        sub_id=sub_id,
        account_id=account_id,
        plan_id=request.get("plan_id", "pro_monthly"),
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        stripe_subscription_id=f"sub_{uuid.uuid4().hex[:8]}"
    )
    db.add(subscription)
    db.commit()
    
    return {
        "account_id": str(account_id),
        "subscription_id": str(sub_id),
        "status": "active"
    }

@router.get("/usage")
async def get_usage_metrics(
    current_user: CurrentUser = Depends(require_tenant_admin()),
    db: Session = Depends(get_db)
):
    """
    Get usage metrics for the Billing Dashboard.
    """
    org_id = current_user.org_id
    org = db.query(Organization).filter(Organization.org_id == org_id).first()
    
    if not org or not org.billing_account_id:
        # Fallback for legacy/demo accounts
        return {
            "plan": {"name": org.plan if org else "free", "status": "active"},
            "metrics": {
                "tokens": {"used": 15000, "limit": 100000},
                "storage": {"used_mb": 45, "limit_mb": 500},
                "properties": {"used": len(org.properties) if org else 0, "limit": 3}
            }
        }

    account = db.query(BillingAccount).filter(BillingAccount.account_id == org.billing_account_id).first()
    subscription = db.query(Subscription).filter(Subscription.account_id == account.account_id).first()
    
    # Mock Usage Data (In real app, query Redis/DB logs)
    return {
        "plan": {
            "name": subscription.plan_id,
            "status": subscription.status,
            "renews_at": subscription.current_period_end,
            "amount": "RM 10,000.00" if "pro" in subscription.plan_id else "RM 0.00"
        },
        "metrics": {
            "tokens": {"used": 124500, "limit": 500000}, # Monthly
            "storage": {"used_mb": 120, "limit_mb": 1000},
            "properties": {"used": len(org.properties), "limit": 3 if "pro" in subscription.plan_id else 1}
        }
    }

@router.post("/unsubscribe")
async def unsubscribe(
    current_user: CurrentUser = Depends(require_tenant_admin()),
    db: Session = Depends(get_db)
):
    """
    Cancel subscription and revoke access.
    """
    org = db.query(Organization).filter(Organization.org_id == current_user.org_id).first()
    if not org or not org.billing_account_id:
        raise HTTPException(status_code=400, detail="No billing account found")
        
    subscription = db.query(Subscription).filter(
        Subscription.account_id == org.billing_account_id,
        Subscription.status == "active"
    ).first()
    
    if not subscription:
        return {"message": "No active subscription to cancel"}
        
    # Update Subscription
    subscription.status = "canceled"
    # End period immediately or at end (User requested 'stop billing', implies immediate or end of cycle)
    # For SaaS, usually end of cycle access, but request implies revoke access.
    # We will mark as canceled and middleware handles revocation.
    
    # Also update Org status for faster middleware checks
    org.subscription_status = "canceled"
    
    db.commit()
    
    return {"message": "Subscription canceled. Access will be revoked."}

@router.post("/report")
async def generate_report(
    current_user: CurrentUser = Depends(require_tenant_admin()),
    db: Session = Depends(get_db)
):
    """
    Generate a CSV report of usage and billing.
    """
    from fastapi.responses import StreamingResponse
    import io
    import csv

    org = db.query(Organization).filter(Organization.org_id == current_user.org_id).first()
    
    # Mock data generation based on Org stats
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["Metric", "Value", "Unit", "Period"])
    cw.writerow(["Organization", org.name, "Name", "N/A"])
    cw.writerow(["Plan", org.plan, "Type", "Current"])
    cw.writerow(["Subscription Status", org.subscription_status, "Status", "Current"])
    
    # Add usage metrics (Mocked for now, but linked to real org structure)
    cw.writerow(["Token Usage", "124500", "Tokens", "Last 30 Days"])
    cw.writerow(["Properties", str(len(org.properties)), "Count", "Current"])
    
    si.seek(0)
    
    return StreamingResponse(
        iter([si.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=billing_report_{org.slug}.csv"}
    )
