
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict

from app.models import Organization, User, Property, Query, ChatSession

class MonitoringService:
    """
    Service for SaaS Controller (Super Admin) monitoring.
    Aggregates data across all tenants.
    """
    
    @staticmethod
    def get_all_tenants(db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get list of tenants with aggregated counts."""
        orgs = db.query(Organization).order_by(Organization.created_at.desc()).offset(skip).limit(limit).all()
        
        results = []
        for org in orgs:
            # Count properties
            prop_count = db.query(Property).filter(Property.org_id == org.org_id).count()
            # Count users
            user_count = db.query(User).filter(User.org_id == org.org_id).count()
            
            results.append({
                "org_id": str(org.org_id),
                "name": org.name,
                "slug": org.slug,
                "plan": org.plan,
                "property_count": prop_count,
                "user_count": user_count,
                "status": org.subscription_status,
                "created_at": org.created_at
            })
        return results

    @staticmethod
    def get_global_stats(db: Session) -> Dict:
        """Get high-level system stats."""
        total_tenants = db.query(Organization).count()
        active_tenants = db.query(Organization).filter(Organization.subscription_status == "active").count()
        total_users = db.query(User).count()
        
        # Last 24h queries
        yesterday = datetime.utcnow() - timedelta(hours=24)
        queries_24h = db.query(Query).filter(Query.timestamp >= yesterday).count()
        
        # Avg Latency 24h
        avg_latency = db.query(func.avg(Query.response_time_ms)).filter(Query.timestamp >= yesterday).scalar() or 0
        
        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "total_users": total_users,
            "total_queries_24h": queries_24h,
            "system_health": "healthy" if avg_latency < 3000 else "degraded",
            "avg_latency_ms": float(avg_latency)
        }

    @staticmethod
    def update_tenant_status(db: Session, org_id: str, status: str) -> bool:
        """Update tenant subscription status."""
        org = db.query(Organization).filter(Organization.org_id == org_id).first()
        if not org:
            return False
        
        org.subscription_status = status
        db.commit()
        return True
