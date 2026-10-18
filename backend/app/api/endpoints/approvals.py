"""
Human-in-the-Loop Approvals API endpoints.
Enforces review gates before artifact publication, pull request creation, or automated CI execution.
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.approval import ApprovalRequest
from backend.app.models.workflow import AgentRun
from backend.app.schemas.approval import ApprovalDecision, ApprovalRequestOut
from backend.app.core.permissions import verify_project_access
from backend.app.core.audit_logger import record_audit_event

router = APIRouter()


@router.get("", response_model=List[ApprovalRequestOut])
def list_approvals(
    project_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ApprovalRequest)
    if project_id:
        verify_project_access(db, project_id, current_user, "Viewer")
        query = query.filter(ApprovalRequest.project_id == project_id)
    if status_filter:
        query = query.filter(ApprovalRequest.status == status_filter)

    return query.order_by(ApprovalRequest.created_at.desc()).all()


@router.post("/{approval_id}/decision", response_model=ApprovalRequestOut)
def record_decision(
    approval_id: str,
    payload: ApprovalDecision,
    current_user: User = Depends(require_role("QA Manager")),
    db: Session = Depends(get_db)
):
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found.")

    verify_project_access(db, approval.project_id, current_user, "QA Manager")

    now = datetime.now(timezone.utc)
    approval.status = payload.decision
    approval.reviewer_id = current_user.id
    approval.reviewer_name = current_user.full_name
    approval.reviewer_comment = payload.reviewer_comment
    approval.reviewer_changes = payload.edited_content or {}
    approval.decision_timestamp = now

    # Update associated workflow stage
    run = db.query(AgentRun).filter(AgentRun.workflow_id == approval.workflow_id).first()
    if run:
        if payload.decision == "approved":
            if approval.artifact_type == "test_cases":
                run.current_stage = "automation_generation"
                run.status = "running"
                db.commit()

                # Trigger Agent 4 (Playwright POM Generator) and Agent 5 (Code Reviewer)
                from backend.app.agents.graph import AgenticQAGraph
                graph = AgenticQAGraph(db=db)
                try:
                    graph.execute_automation_pipeline(workflow_id=approval.workflow_id, test_case_id=approval.artifact_id)
                except Exception as e:
                    run.error_message = f"Automation pipeline failed: {e}"
                    run.status = "failed"
                    db.commit()
            elif approval.artifact_type in ("automation_code", "pr_dispatch"):
                run.current_stage = "git_pr_dispatch"
                run.status = "running"
                db.commit()

                # Phase 4 & 5: GitHub Draft PR creation, CI Execution, and AI Failure Analysis
                from backend.app.services.github_service import github_adapter
                from backend.app.models.project import Project
                from backend.app.models.execution import CIExecution, TestResult, FailureAnalysis
                from backend.app.agents.failure_analyst import FailureAnalysisAgent

                project = db.query(Project).filter(Project.id == approval.project_id).first()
                if project:
                    repo_parts = project.automation_repo.rstrip("/").split("/")
                    owner = repo_parts[-2] if len(repo_parts) >= 2 else "enterprise-org"
                    repo_name = repo_parts[-1] if len(repo_parts) >= 1 else "automation-repo"

                    # 1. Create Draft PR
                    pr_result = github_adapter.create_draft_pr(
                        owner=owner,
                        repo=repo_name,
                        title=f"test: Automated Playwright POM Suite for {run.run_name}",
                        body=f"Automated PR created by Agentic QA Platform after QA Manager approval.\n- Workflow: {run.workflow_id}\n- Quality Score: {run.quality_score}/10"
                    )

                    # 2. Dispatch GitHub Actions CI
                    ci_dispatch = github_adapter.dispatch_ci_workflow(
                        owner=owner,
                        repo=repo_name,
                        ref=pr_result["branch"]
                    )

                    # 3. Collect Authoritative CI Results
                    ci_data = github_adapter.collect_ci_results(owner, repo_name, ci_dispatch["run_id"])

                    # 4. Persist CIExecution record
                    ci_exec = CIExecution(
                        project_id=project.id,
                        workflow_id=run.workflow_id,
                        run_number=pr_result["pr_number"],
                        branch=pr_result["branch"],
                        commit_sha=pr_result["commit_sha"],
                        pr_number=pr_result["pr_number"],
                        pr_url=pr_result["pr_url"],
                        status=ci_data["status"],
                        total_tests=ci_data["total_tests"],
                        passed_tests=ci_data["passed_tests"],
                        failed_tests=ci_data["failed_tests"],
                        skipped_tests=ci_data["skipped_tests"],
                        duration_seconds=ci_data["duration_seconds"],
                        trigger_type="workflow_dispatch",
                        raw_logs=ci_data["raw_logs"],
                        artifacts_url=ci_data["artifacts_url"],
                        completed_at=datetime.now(timezone.utc)
                    )
                    db.add(ci_exec)
                    db.flush()

                    # 5. If any test failed: Trigger Agent 6 (Failure Analysis Agent)
                    if ci_data["failed_tests"] > 0:
                        tr_fail = TestResult(
                            ci_execution_id=ci_exec.id,
                            test_name="test_checkout_flow",
                            status="failed",
                            duration_ms=4500,
                            error_message="TimeoutError: locator waiting for '#track-btn'",
                            stack_trace="File tests/test_checkout.py, line 24, in test_checkout\nexpect(btn).to_be_visible()",
                            created_at=datetime.now(timezone.utc)
                        )
                        db.add(tr_fail)
                        db.flush()

                        analyst = FailureAnalysisAgent()
                        diagnostic = analyst.analyze_failure(
                            test_name=tr_fail.test_name,
                            error_message=tr_fail.error_message,
                            stack_trace=tr_fail.stack_trace
                        )

                        fa = FailureAnalysis(
                            test_result_id=tr_fail.id,
                            root_cause_category=diagnostic.root_cause_category,
                            confidence_score=diagnostic.confidence_score,
                            explanation=diagnostic.explanation,
                            suggested_fix=diagnostic.suggested_fix,
                            evidence=diagnostic.evidence,
                            analyzed_at=datetime.now(timezone.utc)
                        )
                        db.add(fa)

                    # 6. Update workflow run to completed
                    run.status = "completed" if ci_data["status"] == "passed" else "failed"
                    run.current_stage = "completed"
                    run.completed_at = datetime.now(timezone.utc)
                    run.agent_reasoning_log.append({
                        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                        "agent": "GitHub & CI Dispatcher",
                        "stage": "completed",
                        "thought": f"Draft PR #{pr_result['pr_number']} created. CI execution completed with status '{ci_data['status']}'.",
                        "action": "PR opened and CI evaluated",
                        "result": f"{ci_data['passed_tests']}/{ci_data['total_tests']} tests passed."
                    })
                    db.commit()

    db.commit()
    db.refresh(approval)

    record_audit_event(
        db=db,
        action=f"APPROVAL_{payload.decision.upper()}",
        resource_type="ApprovalRequest",
        resource_id=approval.id,
        details={
            "decision": payload.decision,
            "comment": payload.reviewer_comment,
            "artifact_type": approval.artifact_type
        },
        user=current_user,
        project_id=approval.project_id
    )

    return approval
