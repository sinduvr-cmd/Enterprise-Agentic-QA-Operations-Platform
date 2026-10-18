"""
CI Executions and Test Results API endpoints.
Provides authoritative CI outcomes, Playwright execution traces, and AI Failure Analysis.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, get_current_user
from backend.app.models.user import User
from backend.app.models.execution import CIExecution, TestResult, FailureAnalysis
from backend.app.schemas.execution import CIExecutionOut, CIExecutionDetail, FailureAnalysisOut
from backend.app.core.permissions import verify_project_access

router = APIRouter()


@router.get("", response_model=List[CIExecutionOut])
def list_ci_executions(
    project_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(CIExecution)
    if project_id:
        verify_project_access(db, project_id, current_user, "Viewer")
        query = query.filter(CIExecution.project_id == project_id)
    if status_filter:
        query = query.filter(CIExecution.status == status_filter)

    return query.order_by(CIExecution.started_at.desc()).all()


@router.get("/{execution_id}", response_model=CIExecutionDetail)
def get_ci_execution_detail(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    execution = db.query(CIExecution).filter(CIExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found.")

    verify_project_access(db, execution.project_id, current_user, "Viewer")
    return execution


@router.get("/failure-analyses/{test_result_id}", response_model=FailureAnalysisOut)
def get_failure_analysis(
    test_result_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fa = db.query(FailureAnalysis).filter(FailureAnalysis.test_result_id == test_result_id).first()
    if not fa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failure analysis not found.")

    return fa
