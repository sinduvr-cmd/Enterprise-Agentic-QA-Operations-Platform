"""
Role-based access control (RBAC) and Project-level Authorization.
Roles:
- Admin: Full system access across all projects and configurations.
- QA Manager: Project configuration, initiating runs, human approvals, CI trigger.
- QA Engineer: Test case generation, editing, viewing, and starting workflows.
- Viewer: Read-only access to authorized projects and dashboard reports.
"""
from typing import List
from fastapi import HTTPException, status
from backend.app.models.user import User
from backend.app.models.project import ProjectMembership
from sqlalchemy.orm import Session

ROLE_HIERARCHY = {
    "Admin": 4,
    "QA Manager": 3,
    "QA Engineer": 2,
    "Viewer": 1,
}


def check_role_minimum(user_role: str, minimum_required_role: str) -> bool:
    """
    Checks if a user's role satisfies the minimum required level.
    """
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level = ROLE_HIERARCHY.get(minimum_required_role, 999)
    return user_level >= required_level


def enforce_minimum_role(current_user: User, minimum_role: str):
    """
    Raises HTTP 403 if user role does not satisfy the requirement.
    """
    if not check_role_minimum(current_user.role, minimum_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Action requires minimum role '{minimum_role}'. Your current role is '{current_user.role}'."
        )


def verify_project_access(
    db: Session,
    project_id: str,
    user: User,
    required_role: str = "Viewer"
) -> bool:
    """
    Verifies that the user has authorized access to a specific project.
    Admins automatically have access to all projects.
    """
    if user.role == "Admin":
        return True

    membership = db.query(ProjectMembership).filter(
        ProjectMembership.project_id == project_id,
        ProjectMembership.user_id == user.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have access to project '{project_id}'."
        )

    effective_role = membership.role or user.role
    if not check_role_minimum(effective_role, required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Project '{project_id}' requires '{required_role}' permission."
        )

    return True
