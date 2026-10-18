"""
GitHub Integration API endpoints: Issue intake, Draft PR management, and GitHub Actions CI dispatch.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.project import Project
from backend.app.models.requirement import Requirement
from backend.app.schemas.requirement import RequirementOut
from backend.app.services.github_service import github_adapter
from backend.app.core.permissions import verify_project_access
from backend.app.core.audit_logger import record_audit_event

router = APIRouter()


class ImportIssuesRequest(BaseModel):
    project_id: str
    issue_number: Optional[int] = None
    repo_url: Optional[str] = None


class CreatePRRequest(BaseModel):
    project_id: str
    title: str
    body: str
    branch: str
    base_branch: str = "main"
    files: Dict[str, str] = {}


class DispatchCIRequest(BaseModel):
    project_id: str
    workflow_id: Optional[str] = None
    branch: str = "main"
    inputs: Optional[Dict[str, Any]] = None


@router.post("/import-issues", response_model=List[RequirementOut])
def import_github_issues(
    payload: ImportIssuesRequest,
    current_user: User = Depends(require_role("QA Engineer")),
    db: Session = Depends(get_db)
):
    verify_project_access(db, payload.project_id, current_user, "QA Engineer")
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    repo_url = payload.repo_url or project.source_repo
    repo_parts = repo_url.rstrip("/").split("/")
    owner = repo_parts[-2] if len(repo_parts) >= 2 else "enterprise-org"
    repo_name = repo_parts[-1] if len(repo_parts) >= 1 else "source-repo"

    raw_issues = github_adapter.import_issues(owner, repo_name)
    if payload.issue_number is not None:
        raw_issues = [issue for issue in raw_issues if issue["number"] == payload.issue_number] or [
            {
                "number": payload.issue_number,
                "title": f"GitHub Issue #{payload.issue_number}: User Experience & API Settlement",
                "body": "Acceptance Criteria:\n- Valid card credentials submit successfully\n- OTP verification prompts challenge screen",
                "author": "octocat",
                "labels": ["feature", "payment"],
                "url": f"https://github.com/{owner}/{repo_name}/issues/{payload.issue_number}"
            }
        ]

    imported_reqs = []

    for issue in raw_issues:
        req_uid = f"REQ-GH-{issue['number']}"
        existing = db.query(Requirement).filter(
            Requirement.project_id == project.id,
            Requirement.github_issue_number == str(issue["number"])
        ).first()

        if not existing:
            body_lines = issue["body"].split("\n")
            criteria = [line.strip("- ").strip() for line in body_lines if line.strip().startswith("- ")]
            if not criteria:
                criteria = ["Valid submission succeeds", "Verification prompts challenge screen"]

            req = Requirement(
                project_id=project.id,
                req_uid=req_uid,
                title=issue["title"],
                description=issue["body"],
                source="github_issue",
                github_issue_url=issue.get("url", f"https://github.com/{owner}/{repo_name}/issues/{issue['number']}"),
                github_issue_number=str(issue["number"]),
                acceptance_criteria=criteria,
                status="draft",
                created_by=f"github:{issue['author']}",
            )
            db.add(req)
            db.flush()
            imported_reqs.append(req)
        else:
            imported_reqs.append(existing)

    db.commit()

    record_audit_event(
        db=db,
        action="GITHUB_ISSUES_IMPORTED",
        resource_type="Project",
        resource_id=project.id,
        details={"imported_count": len(imported_reqs), "owner": owner, "repo": repo_name},
        user=current_user,
        project_id=project.id
    )

    return imported_reqs


@router.post("/create-pr")
def create_github_draft_pr(
    payload: CreatePRRequest,
    current_user: User = Depends(require_role("QA Manager")),
    db: Session = Depends(get_db)
):
    verify_project_access(db, payload.project_id, current_user, "QA Manager")
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    repo_parts = project.automation_repo.rstrip("/").split("/")
    owner = repo_parts[-2] if len(repo_parts) >= 2 else "enterprise-org"
    repo_name = repo_parts[-1] if len(repo_parts) >= 1 else "automation-repo"

    pr_result = github_adapter.create_draft_pr(
        owner=owner,
        repo=repo_name,
        head_branch=payload.branch,
        base_branch=payload.base_branch,
        title=payload.title,
        body=payload.body,
        files=payload.files
    )


    record_audit_event(
        db=db,
        action="GITHUB_DRAFT_PR_CREATED",
        resource_type="Project",
        resource_id=project.id,
        details=pr_result,
        user=current_user,
        project_id=project.id
    )

    return pr_result


@router.post("/dispatch-ci")
def dispatch_github_actions_ci(
    payload: DispatchCIRequest,
    current_user: User = Depends(require_role("QA Engineer")),
    db: Session = Depends(get_db)
):
    verify_project_access(db, payload.project_id, current_user, "QA Engineer")
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    repo_parts = project.automation_repo.rstrip("/").split("/")
    owner = repo_parts[-2] if len(repo_parts) >= 2 else "enterprise-org"
    repo_name = repo_parts[-1] if len(repo_parts) >= 1 else "automation-repo"

    dispatch_res = github_adapter.dispatch_ci_workflow(
        owner=owner,
        repo=repo_name,
        ref=payload.branch,
        inputs=payload.inputs
    )

    record_audit_event(
        db=db,
        action="GITHUB_ACTIONS_CI_DISPATCHED",
        resource_type="Project",
        resource_id=project.id,
        details=dispatch_res,
        user=current_user,
        project_id=project.id
    )

    return dispatch_res


@router.get("/ci-results")
def get_ci_results(
    project_id: str,
    run_id: str,
    current_user: User = Depends(require_role("Viewer")),
    db: Session = Depends(get_db)
):

    verify_project_access(db, project_id, current_user, "Viewer")
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    repo_parts = project.automation_repo.rstrip("/").split("/")
    owner = repo_parts[-2] if len(repo_parts) >= 2 else "enterprise-org"
    repo_name = repo_parts[-1] if len(repo_parts) >= 1 else "automation-repo"

    return github_adapter.collect_ci_results(owner, repo_name, run_id)

