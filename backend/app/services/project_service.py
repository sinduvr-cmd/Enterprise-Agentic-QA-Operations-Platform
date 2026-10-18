"""
Project management business logic: creation, listing, updating, archiving, and stats calculation.
"""
import re
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from backend.app.models.project import Project, ProjectMembership
from backend.app.models.workflow import AgentRun
from backend.app.models.test_case import TestCase
from backend.app.models.user import User
from backend.app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, ProjectDetail
from backend.app.core.audit_logger import record_audit_event


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return f"proj-{slug}" if not slug.startswith("proj-") else slug


def get_project_stats(db: Session, project_id: str) -> dict:
    active_runs = db.query(func.count(AgentRun.id)).filter(
        AgentRun.project_id == project_id,
        AgentRun.status.in_(["running", "awaiting_approval"])
    ).scalar() or 0

    total_tests = db.query(func.count(TestCase.id)).filter(
        TestCase.project_id == project_id
    ).scalar() or 0

    automated_tests = db.query(func.count(TestCase.id)).filter(
        TestCase.project_id == project_id,
        TestCase.is_automated.is_(True)
    ).scalar() or 0

    coverage = round((automated_tests / total_tests * 100), 1) if total_tests > 0 else 0.0

    return {
        "active_runs_count": active_runs,
        "test_cases_count": total_tests,
        "automation_coverage": coverage
    }


def list_projects(
    db: Session,
    user: User,
    include_archived: bool = False
) -> List[ProjectOut]:
    query = db.query(Project)
    if not include_archived:
        query = query.filter(Project.is_archived.is_(False))

    # Project-level access filtering: Admins see all; other roles see only assigned projects
    if user.role != "Admin":
        query = query.join(ProjectMembership).filter(ProjectMembership.user_id == user.id)

    projects = query.order_by(Project.created_at.desc()).all()

    result = []
    for proj in projects:
        stats = get_project_stats(db, proj.id)
        proj_out = ProjectOut(
            id=proj.id,
            name=proj.name,
            description=proj.description,
            source_repo=proj.source_repo,
            automation_repo=proj.automation_repo,
            default_branch=proj.default_branch,
            framework_config=proj.framework_config,
            is_archived=proj.is_archived,
            created_at=proj.created_at,
            updated_at=proj.updated_at,
            **stats
        )
        result.append(proj_out)

    return result


def get_project_by_id(db: Session, project_id: str) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()


def create_project(
    db: Session,
    payload: ProjectCreate,
    creator: User
) -> Project:
    project_id = payload.id or slugify(payload.name)

    existing = db.query(Project).filter(Project.id == project_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with ID '{project_id}' already exists."
        )

    framework_config = payload.framework_config or {
        "framework": "playwright-python",
        "test_runner": "pytest",
        "pattern": "Page Object Model",
        "base_url": "https://staging.example.com",
        "browsers": ["chromium", "firefox", "webkit"],
        "headless": True
    }

    project = Project(
        id=project_id,
        name=payload.name,
        description=payload.description,
        source_repo=payload.source_repo,
        automation_repo=payload.automation_repo,
        default_branch=payload.default_branch,
        framework_config=framework_config,
        is_archived=False,
    )
    db.add(project)

    # Assign creator as Admin/Manager membership
    membership = ProjectMembership(
        project_id=project_id,
        user_id=creator.id,
        role="Admin" if creator.role == "Admin" else "QA Manager"
    )
    db.add(membership)

    db.commit()
    db.refresh(project)

    record_audit_event(
        db=db,
        action="PROJECT_CREATED",
        resource_type="Project",
        resource_id=project.id,
        details={"name": project.name, "source_repo": project.source_repo},
        user=creator,
        project_id=project.id
    )

    return project


def update_project(
    db: Session,
    project_id: str,
    payload: ProjectUpdate,
    user: User
) -> Project:
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(project, field, val)

    db.commit()
    db.refresh(project)

    record_audit_event(
        db=db,
        action="PROJECT_UPDATED",
        resource_type="Project",
        resource_id=project.id,
        details=update_data,
        user=user,
        project_id=project.id
    )

    return project
