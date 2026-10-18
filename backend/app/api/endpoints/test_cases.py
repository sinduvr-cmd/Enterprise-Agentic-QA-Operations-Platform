"""
Test Cases API endpoints.
Provides filtering and inspection of AI-generated manual test cases and quality evaluations.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, get_current_user
from backend.app.models.user import User
from backend.app.models.test_case import TestCase, QualityEvaluation
from backend.app.schemas.test_case import TestCaseOut, QualityEvaluationOut
from backend.app.core.permissions import verify_project_access

router = APIRouter()


@router.get("", response_model=List[TestCaseOut])
def list_test_cases(
    project_id: Optional[str] = Query(None),
    requirement_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(TestCase)
    if project_id:
        verify_project_access(db, project_id, current_user, "Viewer")
        query = query.filter(TestCase.project_id == project_id)
    if requirement_id:
        query = query.filter(TestCase.requirement_id == requirement_id)
    if category:
        query = query.filter(TestCase.category == category)
    if priority:
        query = query.filter(TestCase.priority == priority)
    if status_filter:
        query = query.filter(TestCase.status == status_filter)

    return query.order_by(TestCase.created_at.desc()).all()


@router.get("/{test_case_id}", response_model=TestCaseOut)
def get_test_case(
    test_case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not tc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found.")

    verify_project_access(db, tc.project_id, current_user, "Viewer")
    return tc


@router.get("/{test_case_id}/evaluations", response_model=List[QualityEvaluationOut])
def get_test_case_evaluations(
    test_case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not tc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found.")

    verify_project_access(db, tc.project_id, current_user, "Viewer")
    return db.query(QualityEvaluation).filter(QualityEvaluation.test_case_id == test_case_id).all()
