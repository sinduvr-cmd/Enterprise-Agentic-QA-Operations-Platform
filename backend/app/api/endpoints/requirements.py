"""
Requirements API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.requirement import Requirement
from backend.app.schemas.requirement import RequirementCreate, RequirementOut
from backend.app.core.permissions import verify_project_access
from backend.app.core.audit_logger import record_audit_event

router = APIRouter()


@router.get("", response_model=List[RequirementOut])
def get_requirements(
    project_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Requirement)
    if project_id:
        verify_project_access(db, project_id, current_user, "Viewer")
        query = query.filter(Requirement.project_id == project_id)
    return query.order_by(Requirement.created_at.desc()).all()


@router.post("", response_model=RequirementOut, status_code=status.HTTP_201_CREATED)
def post_requirement(
    payload: RequirementCreate,
    current_user: User = Depends(require_role("QA Engineer")),
    db: Session = Depends(get_db)
):
    verify_project_access(db, payload.project_id, current_user, "QA Engineer")

    # Generate sequential requirement UID if not provided
    count = db.query(Requirement).filter(Requirement.project_id == payload.project_id).count()
    req_uid = payload.req_uid or f"REQ-{payload.project_id.split('-')[-1].upper()[:3]}-{count + 101:03d}"

    req = Requirement(
        project_id=payload.project_id,
        req_uid=req_uid,
        title=payload.title,
        description=payload.description,
        source=payload.source,
        github_issue_url=payload.github_issue_url,
        github_issue_number=payload.github_issue_number,
        acceptance_criteria=payload.acceptance_criteria or [],
        status="draft",
        created_by=current_user.email,
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    record_audit_event(
        db=db,
        action="REQUIREMENT_CREATED",
        resource_type="Requirement",
        resource_id=req.id,
        details={"req_uid": req.req_uid, "title": req.title, "source": req.source},
        user=current_user,
        project_id=req.project_id
    )

    return req
