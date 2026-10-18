"""
Dashboard API endpoints: Metrics, summary cards, recent runs, agent activity timeline, trends.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, get_current_user
from backend.app.models.user import User
from backend.app.schemas.dashboard import DashboardOverviewResponse
from backend.app.services.dashboard_service import get_dashboard_overview

router = APIRouter()


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_data(
    project_id: Optional[str] = Query(None, description="Optional project filter"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns aggregated dashboard metrics matching the reference operations design.
    """
    return get_dashboard_overview(db=db, project_id=project_id)
