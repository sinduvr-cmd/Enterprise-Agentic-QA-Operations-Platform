"""
Pydantic schemas for Requirement ingestion and management.
"""
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class RequirementCreate(BaseModel):
    project_id: str
    req_uid: Optional[str] = None
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    source: str = "manual"  # manual | github_issue | jira
    github_issue_url: Optional[str] = None
    github_issue_number: Optional[str] = None
    acceptance_criteria: List[str] = []


class RequirementOut(BaseModel):
    id: str
    project_id: str
    req_uid: str
    title: str
    description: str
    source: str
    github_issue_url: Optional[str] = None
    github_issue_number: Optional[str] = None
    acceptance_criteria: List[str] = []
    extracted_scenarios: List[Any] = []
    ambiguities: List[Any] = []
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
