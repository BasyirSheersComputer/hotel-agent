"""
Copyright (c) 2025 Sheers Software Sdn. Bhd.
All Rights Reserved.

Dashboard API Endpoints
Provides metrics and analytics data for the performance dashboard.
Requires admin role in SaaS mode.
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.metrics_service import get_metrics_service
from app.middleware.auth import get_current_user, CurrentUser, require_admin
from app.config.settings import DEMO_MODE
from fastapi.responses import Response
from datetime import datetime

# All dashboard routes require admin role
router = APIRouter(dependencies=[Depends(require_admin())])

class MetricsSummary(BaseModel):
    """Summary metrics model"""
    total_queries: int
    avg_response_time_ms: float
    success_rate: float
    unique_agents: int
    period_hours: int
    
    # New fields
    accuracy_percent: float
    internal_accuracy_percent: float
    external_accuracy_percent: float
    aht_reduction_percent: float
    aht_delta_percent: float
    
    rag_count: int
    rag_percentage: float
    maps_count: int
    maps_percentage: float
    
    tokens_used: int
    estimated_cost: float
    rate_limit_status: str
    cost_breakdown: str
    
    # New ROI Metrics
    avg_sentiment: float
    avg_csat: float
    booking_leads: int
    upsell_opportunities: int
    total_revenue_potential: float
    sop_compliance_rate: float
    fcr_rate: float
    booking_conversion_rate: float

class CategoryMetric(BaseModel):
    """Question category metric"""
    category: str
    count: int
    avg_ai_time: float # Renamed from avg_response_time_ms
    accuracy: float # Added

class HourlyTrend(BaseModel):
    """Hourly trend data"""
    time: str # Renamed from hour
    queryVolume: int # Renamed from query_count
    avg_response_time_ms: float
    success_rate: float

class AgentMetric(BaseModel):
    """Agent performance metric"""
    name: str # Renamed from agent_id
    queryCount: int # Renamed
    avgTimeMs: float # Renamed
    accuracyPercent: float # Added
    lastActive: str # Renamed

class SourceMetric(BaseModel):
    """Source distribution metric"""
    source: str
    count: int
    percentage: float

@router.get("/metrics/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    request: Request,
    hours: int = Query(default=24, ge=1, le=744, description="Hours to look back (1-744)"),
    start_date: Optional[str] = Query(None, description="ISO Start Date (YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="ISO End Date (YYYY-MM-DDTHH:MM:SS)")
):
    """
    Get summary metrics for the dashboard
    """
    try:
        org_id = getattr(request.state, "org_id", None)
        service = get_metrics_service()
        
        # Parse Dates
        dt_start = datetime.fromisoformat(start_date) if start_date else None
        dt_end = datetime.fromisoformat(end_date) if end_date else None
        
        data = service.get_summary_metrics(hours=hours, org_id=org_id, start_date=dt_start, end_date=dt_end)
        return MetricsSummary(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics summary: {str(e)}")

@router.get("/metrics/categories", response_model=List[CategoryMetric])
async def get_question_categories(
    request: Request,
    hours: int = Query(default=24, ge=1, le=744),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get breakdown of questions by category
    """
    try:
        org_id = getattr(request.state, "org_id", None)
        service = get_metrics_service()
        dt_start = datetime.fromisoformat(start_date) if start_date else None
        dt_end = datetime.fromisoformat(end_date) if end_date else None
        
        data = service.get_question_categories(hours=hours, org_id=org_id, start_date=dt_start, end_date=dt_end)
        return [CategoryMetric(**item) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")

@router.get("/metrics/trends", response_model=List[HourlyTrend])
async def get_hourly_trends(
    request: Request,
    hours: int = Query(default=24, ge=1, le=744),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get hourly query trends
    """
    try:
        org_id = getattr(request.state, "org_id", None)
        service = get_metrics_service()
        dt_start = datetime.fromisoformat(start_date) if start_date else None
        dt_end = datetime.fromisoformat(end_date) if end_date else None
        
        data = service.get_hourly_trends(hours=hours, org_id=org_id, start_date=dt_start, end_date=dt_end)
        return [HourlyTrend(**item) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {str(e)}")

@router.get("/metrics/agents", response_model=List[AgentMetric])
async def get_agent_performance(
    request: Request,
    hours: int = Query(default=24, ge=1, le=744),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get performance metrics per agent
    """
    try:
        org_id = getattr(request.state, "org_id", None)
        service = get_metrics_service()
        dt_start = datetime.fromisoformat(start_date) if start_date else None
        dt_end = datetime.fromisoformat(end_date) if end_date else None

        data = service.get_agent_performance(hours=hours, org_id=org_id, start_date=dt_start, end_date=dt_end)
        return [AgentMetric(**item) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch agent metrics: {str(e)}")

@router.get("/metrics/sources", response_model=List[SourceMetric])
async def get_source_distribution(
    request: Request,
    hours: int = Query(default=24, ge=1, le=744)
):
    """
    Get distribution of query sources (RAG, Maps, etc.)
    """
    try:
        org_id = getattr(request.state, "org_id", None)
        service = get_metrics_service()
        data = service.get_source_distribution(hours=hours, org_id=org_id)
        return [SourceMetric(**item) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch source distribution: {str(e)}")

@router.get("/reports/export")
async def export_report(
    request: Request,
    hours: int = Query(default=24),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Generate and download CSV report for CFO/Accounts
    """
    try:
        org_id = getattr(request.state, "org_id", None)
        service = get_metrics_service()
        dt_start = datetime.fromisoformat(start_date) if start_date else None
        dt_end = datetime.fromisoformat(end_date) if end_date else None
        
        csv_content = service.generate_csv_report(hours=hours, org_id=org_id, start_date=dt_start, end_date=dt_end)
        
        filename = f"cfo_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        
        # Encode with BOM for Excel compatibility (utf-8-sig)
        return Response(
            content=csv_content.encode('utf-8-sig'),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")

@router.get("/reports/export-pdf")
async def export_pdf_report(
    request: Request,
    hours: int = Query(default=24),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Generate and download PDF report
    """
    try:
        org_id = getattr(request.state, "org_id", None)
        service = get_metrics_service()
        dt_start = datetime.fromisoformat(start_date) if start_date else None
        dt_end = datetime.fromisoformat(end_date) if end_date else None
        
        pdf_content = service.generate_pdf_report(hours=hours, org_id=org_id, start_date=dt_start, end_date=dt_end)
        
        filename = f"cfo_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export PDF: {str(e)}")
