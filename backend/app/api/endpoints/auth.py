"""
Authentication API endpoints: Login, Current User profile, Role list.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.api.deps import get_db, get_current_user
from backend.app.models.user import User
from backend.app.schemas.user import UserOut, Token
from backend.app.core.security import verify_password, create_access_token

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class SwitchRoleRequest(BaseModel):
    role: str  # Admin | QA Manager | QA Engineer | Viewer


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or (user.hashed_password and not verify_password(payload.password, user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    token = create_access_token({"sub": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=List[UserOut])
def list_available_users(db: Session = Depends(get_db)):
    """
    Returns list of seeded users to facilitate instant demo switching.
    """
    return db.query(User).all()
