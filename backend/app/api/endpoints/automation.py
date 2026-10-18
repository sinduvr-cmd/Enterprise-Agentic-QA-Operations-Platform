"""
Automation Scripts API endpoints.
Provides endpoints to inspect generated Python Playwright Page Object Model suites,
page objects, fixtures, and code review safety reports.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.api.deps import get_db, get_current_user
from backend.app.models.user import User
from backend.app.models.automation_script import AutomationScript
from backend.app.core.permissions import verify_project_access

router = APIRouter()


class AutomationScriptOut(BaseModel):
    id: str
    project_id: str
    test_case_id: str
    file_path: str
    class_name: Optional[str] = None
    language: str
    framework: str
    review_status: str
    reviewer_notes: Optional[str] = None
    syntax_valid: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AutomationScriptDetail(AutomationScriptOut):
    test_code: str
    page_objects: Dict[str, str] = {}
    fixtures: Dict[str, str] = {}


@router.get("/scripts", response_model=List[AutomationScriptOut])
def list_automation_scripts(
    project_id: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(AutomationScript)
    if project_id:
        verify_project_access(db, project_id, current_user, "Viewer")
        query = query.filter(AutomationScript.project_id == project_id)
    if review_status:
        query = query.filter(AutomationScript.review_status == review_status)

    return query.order_by(AutomationScript.created_at.desc()).all()


@router.get("/scripts/{script_id}", response_model=AutomationScriptDetail)
def get_automation_script(
    script_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    script = db.query(AutomationScript).filter(AutomationScript.id == script_id).first()
    if not script:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation script not found.")

    verify_project_access(db, script.project_id, current_user, "Viewer")
    return script
