"""
Pydantic schemas for User authentication and profiles.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    full_name: str
    role: str = "QA Engineer"
    is_active: bool = True


class UserCreate(UserBase):
    password: Optional[str] = "password123"


class UserOut(UserBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
