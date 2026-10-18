"""
Project management API endpoints: Create, List, View, Update, and Archive.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.project import Project
from backend.app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, ProjectDetail
from backend.app.services.project_service import (
    list_projects,
    get_project_by_id,
    create_project,
    update_project,
    get_project_stats
)
from backend.app.core.permissions import verify_project_access
from backend.app.core.audit_logger import record_audit_event

router = APIRouter()


@router.get("", response_model=List[ProjectOut])
def get_projects(
    include_archived: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all projects accessible by current user.
    """
    return list_projects(db=db, user=current_user, include_archived=include_archived)


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def post_project(
    payload: ProjectCreate,
    current_user: User = Depends(require_role("QA Manager")),
    db: Session = Depends(get_db)
):
    """
    Registers a new project with source and automation repositories.
    """
    project = create_project(db=db, payload=payload, creator=current_user)
    stats = get_project_stats(db, project.id)
    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        source_repo=project.source_repo,
        automation_repo=project.automation_repo,
        default_branch=project.default_branch,
        framework_config=project.framework_config,
        is_archived=project.is_archived,
        created_at=project.created_at,
        updated_at=project.updated_at,
        **stats
    )


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_project_access(db, project_id, current_user, required_role="Viewer")
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    stats = get_project_stats(db, project.id)
    return ProjectDetail(
        id=project.id,
        name=project.name,
        description=project.description,
        source_repo=project.source_repo,
        automation_repo=project.automation_repo,
        default_branch=project.default_branch,
        framework_config=project.framework_config,
        is_archived=project.is_archived,
        created_at=project.created_at,
        updated_at=project.updated_at,
        memberships=project.memberships,
        **stats
    )


@router.put("/{project_id}", response_model=ProjectOut)
def put_project(
    project_id: str,
    payload: ProjectUpdate,
    current_user: User = Depends(require_role("QA Manager")),
    db: Session = Depends(get_db)
):
    verify_project_access(db, project_id, current_user, required_role="QA Manager")
    project = update_project(db=db, project_id=project_id, payload=payload, user=current_user)
    stats = get_project_stats(db, project.id)
    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        source_repo=project.source_repo,
        automation_repo=project.automation_repo,
        default_branch=project.default_branch,
        framework_config=project.framework_config,
        is_archived=project.is_archived,
        created_at=project.created_at,
        updated_at=project.updated_at,
        **stats
    )


@router.patch("/{project_id}/archive", response_model=ProjectOut)
def toggle_archive_project(
    project_id: str,
    current_user: User = Depends(require_role("QA Manager")),
    db: Session = Depends(get_db)
):
    verify_project_access(db, project_id, current_user, required_role="QA Manager")
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    project.is_archived = not project.is_archived
    db.commit()
    db.refresh(project)

    action = "PROJECT_ARCHIVED" if project.is_archived else "PROJECT_UNARCHIVED"
    record_audit_event(
        db=db,
        action=action,
        resource_type="Project",
        resource_id=project.id,
        details={"is_archived": project.is_archived},
        user=current_user,
        project_id=project.id
    )

    stats = get_project_stats(db, project.id)
    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        source_repo=project.source_repo,
        automation_repo=project.automation_repo,
        default_branch=project.default_branch,
        framework_config=project.framework_config,
        is_archived=project.is_archived,
        created_at=project.created_at,
        updated_at=project.updated_at,
        **stats
    )
