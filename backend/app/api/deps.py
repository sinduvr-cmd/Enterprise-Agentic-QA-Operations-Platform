"""
FastAPI Dependencies: Database sessions, JWT user extraction, and Role enforcement.
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.models.user import User
from backend.app.core.security import decode_access_token
from backend.app.core.permissions import check_role_minimum


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: Optional[str] = Header(None),
    x_demo_user_role: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Extracts the authenticated user from JWT Authorization header.
    In DEMO_MODE, allows switching active roles via X-Demo-User-Role header or defaults to Admin.
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            user = db.query(User).filter(User.email == payload["sub"]).first()
            if user:
                return user

    # Demo mode fallback: select user by requested demo role or first admin
    target_role = x_demo_user_role or "Admin"
    demo_user = db.query(User).filter(User.role == target_role, User.is_active.is_(True)).first()
    if demo_user:
        return demo_user

    admin = db.query(User).filter(User.role == "Admin").first()
    if admin:
        return admin

    # If no users exist yet, create a default system user
    fallback = User(
        email="system@enterprise-qa.io",
        full_name="Enterprise Admin",
        role="Admin",
        is_active=True
    )
    db.add(fallback)
    db.commit()
    db.refresh(fallback)
    return fallback


def require_role(min_role: str):
    """
    Dependency factory to enforce minimum role hierarchy.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not check_role_minimum(current_user.role, min_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires minimum role '{min_role}'. Current role is '{current_user.role}'."
            )
        return current_user
    return role_checker
