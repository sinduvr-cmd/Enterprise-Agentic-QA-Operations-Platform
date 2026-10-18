"""
Audit Logs API endpoints for governance and compliance.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.audit import AuditLog

router = APIRouter()


class AuditLogOut(BaseModel):
    id: str
    user_email: Optional[str] = None
    project_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: str
    details: dict
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=List[AuditLogOut])
def get_audit_logs(
    project_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    current_user: User = Depends(require_role("QA Engineer")),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if project_id:
        query = query.filter(AuditLog.project_id == project_id)
    if action:
        query = query.filter(AuditLog.action == action)

    return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
