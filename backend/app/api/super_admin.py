
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.database import get_db
from app.middleware.auth import get_current_user, CurrentUser, require_super_admin
from app.models import Organization, User, Property
from app.services.monitoring import MonitoringService

router = APIRouter(
    prefix="/api/super-admin",
    tags=["Super Admin - SaaS Controller"],
    dependencies=[Depends(require_super_admin())]
)

# Pydantic Models
class TenantOverview(BaseModel):
    org_id: str
    name: str
    slug: str
    plan: str
    property_count: int
    user_count: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class GlobalStats(BaseModel):
    total_tenants: int
    active_tenants: int
    total_users: int
    total_queries_24h: int
    system_health: str
    avg_latency_ms: float

@router.get("/tenants", response_model=List[TenantOverview])
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all tenants with summary metrics."""
    return MonitoringService.get_all_tenants(db, skip, limit)

@router.get("/stats", response_model=GlobalStats)
def get_global_stats(db: Session = Depends(get_db)):
    """Get system-wide health and usage statistics."""
    return MonitoringService.get_global_stats(db)

@router.post("/tenant/{org_id}/suspend")
def suspend_tenant(org_id: str, db: Session = Depends(get_db)):
    """Suspend a tenant (e.g. for non-payment)."""
    success = MonitoringService.update_tenant_status(db, org_id, "suspended")
    if not success:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"message": "Tenant suspended"}

@router.post("/tenant/{org_id}/activate")
def activate_tenant(org_id: str, db: Session = Depends(get_db)):
    """Activate a tenant."""
    success = MonitoringService.update_tenant_status(db, org_id, "active")
    if not success:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"message": "Tenant activated"}
