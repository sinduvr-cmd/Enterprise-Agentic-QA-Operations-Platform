"""
Pydantic schemas for Project lifecycle, configuration, and membership.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class FrameworkConfig(BaseModel):
    framework: str = "playwright-python"
    test_runner: str = "pytest"
    pattern: str = "Page Object Model"
    base_url: str = "https://staging.example.com"
    browsers: List[str] = ["chromium", "firefox", "webkit"]
    headless: bool = True


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    source_repo: str = Field(..., description="e.g. https://github.com/org/checkout-service")
    automation_repo: str = Field(..., description="e.g. https://github.com/org/qa-automation-suite")
    default_branch: str = "main"
    framework_config: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    id: Optional[str] = None  # Auto-generated slug if omitted


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    source_repo: Optional[str] = None
    automation_repo: Optional[str] = None
    default_branch: Optional[str] = None
    framework_config: Optional[Dict[str, Any]] = None
    is_archived: Optional[bool] = None


class ProjectMembershipOut(BaseModel):
    id: str
    user_id: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectOut(ProjectBase):
    id: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    active_runs_count: int = 0
    test_cases_count: int = 0
    automation_coverage: float = 0.0

    model_config = {"from_attributes": True}


class ProjectDetail(ProjectOut):
    memberships: List[ProjectMembershipOut] = []
