"""
Workflows and Agent Runs API endpoints.
Provides endpoints to trigger new QA runs, run LangGraph cyclic loops, inspect agent reasoning timelines, and query checkpoints.
"""
from datetime import datetime, timezone
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.project import Project
from backend.app.models.requirement import Requirement
from backend.app.models.workflow import AgentRun, WorkflowCheckpoint
from backend.app.schemas.workflow import AgentRunCreate, AgentRunOut
from backend.app.core.permissions import verify_project_access
from backend.app.core.audit_logger import record_audit_event
from backend.app.agents.graph import AgenticQAGraph

router = APIRouter()


@router.get("", response_model=List[AgentRunOut])
def list_runs(
    project_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(AgentRun)
    if project_id:
        verify_project_access(db, project_id, current_user, "Viewer")
        query = query.filter(AgentRun.project_id == project_id)
    if status_filter:
        query = query.filter(AgentRun.status == status_filter)

    return query.order_by(AgentRun.started_at.desc()).all()


@router.post("", response_model=AgentRunOut, status_code=status.HTTP_201_CREATED)
def trigger_new_qa_run(
    payload: AgentRunCreate,
    current_user: User = Depends(require_role("QA Engineer")),
    db: Session = Depends(get_db)
):
    """
    Triggers an autonomous Agentic QA workflow:
    Requirement Intake -> Requirement Analyzer -> Test Case Generator -> Critic Evaluator Loop
    """
    verify_project_access(db, payload.project_id, current_user, "QA Engineer")

    proj = db.query(Project).filter(Project.id == payload.project_id).first()
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    now = datetime.now(timezone.utc)
    workflow_id = f"wf-{payload.project_id.split('-')[-1][:3]}-{uuid.uuid4().hex[:6]}"
    run_name = payload.run_name or f"QA Run: {proj.name} ({now.strftime('%b %d %H:%M')})"

    req_title = "User Story Analysis"
    req_desc = payload.requirement_text or f"Automated test generation suite for {proj.name}"
    criteria = payload.acceptance_criteria or []

    if payload.requirement_id:
        req = db.query(Requirement).filter(Requirement.id == payload.requirement_id).first()
        if req:
            req_title = req.title
            req_desc = req.description
            criteria = req.acceptance_criteria or []

    # Initialize AgentRun record
    run = AgentRun(
        workflow_id=workflow_id,
        project_id=payload.project_id,
        requirement_id=payload.requirement_id,
        run_name=run_name,
        current_stage="requirement_analysis",
        status="running",
        quality_score=0.0,
        critic_attempts=0,
        agent_reasoning_log=[],
        started_at=now,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Initialize Graph and run cyclic loop until approval gate
    graph = AgenticQAGraph(db=db)
    graph.create_workflow(
        project_id=payload.project_id,
        workflow_id=workflow_id,
        run_name=run_name,
        requirement_title=req_title,
        requirement_description=req_desc,
        acceptance_criteria=criteria,
        requirement_id=payload.requirement_id
    )

    # Execute autonomous cycle (Requirement Analyzer -> Generator -> Critic Evaluator loop)
    final_state = graph.run_until_approval_or_complete(workflow_id)

    db.refresh(run)

    record_audit_event(
        db=db,
        action="AGENT_RUN_CYCLE_COMPLETED",
        resource_type="AgentRun",
        resource_id=run.id,
        details={
            "workflow_id": workflow_id,
            "stage": run.current_stage,
            "quality_score": run.quality_score,
            "attempts": run.critic_attempts
        },
        user=current_user,
        project_id=run.project_id
    )

    return run


@router.get("/{run_id}", response_model=AgentRunOut)
def get_run_detail(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    run = db.query(AgentRun).filter(
        (AgentRun.id == run_id) | (AgentRun.workflow_id == run_id)
    ).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")

    verify_project_access(db, run.project_id, current_user, "Viewer")
    return run


@router.get("/{run_id}/checkpoints")
def get_run_checkpoints(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    run = db.query(AgentRun).filter(
        (AgentRun.id == run_id) | (AgentRun.workflow_id == run_id)
    ).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")

    verify_project_access(db, run.project_id, current_user, "Viewer")
    checkpoints = db.query(WorkflowCheckpoint).filter(
        WorkflowCheckpoint.workflow_id == run.workflow_id
    ).order_by(WorkflowCheckpoint.created_at.asc()).all()

    return [
        {
            "id": cp.id,
            "step_name": cp.step_name,
            "created_at": cp.created_at,
            "state_summary": {
                "stage": cp.state_payload.get("current_stage"),
                "status": cp.state_payload.get("status"),
                "quality_score": cp.state_payload.get("quality_score"),
                "critic_attempts": cp.state_payload.get("critic_attempts")
            }
        }
        for cp in checkpoints
    ]


@router.post("/{run_id}/step", response_model=AgentRunOut)
def execute_workflow_step(
    run_id: str,
    current_user: User = Depends(require_role("QA Engineer")),
    db: Session = Depends(get_db)
):
    """
    Advances the LangGraph state machine by exactly one step.
    """
    run = db.query(AgentRun).filter(
        (AgentRun.id == run_id) | (AgentRun.workflow_id == run_id)
    ).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")

    verify_project_access(db, run.project_id, current_user, "QA Engineer")

    graph = AgenticQAGraph(db=db)
    graph.run_step(run.workflow_id)
    db.refresh(run)
    return run


@router.post("/{run_id}/cancel", response_model=AgentRunOut)
def cancel_run(
    run_id: str,
    current_user: User = Depends(require_role("QA Manager")),
    db: Session = Depends(get_db)
):
    run = db.query(AgentRun).filter(
        (AgentRun.id == run_id) | (AgentRun.workflow_id == run_id)
    ).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found.")

    verify_project_access(db, run.project_id, current_user, "QA Manager")

    run.status = "failed"
    run.error_message = f"Cancelled by user {current_user.email}."
    run.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)

    record_audit_event(
        db=db,
        action="AGENT_RUN_CANCELLED",
        resource_type="AgentRun",
        resource_id=run.id,
        details={"reason": "User manual cancellation"},
        user=current_user,
        project_id=run.project_id
    )

    return run
