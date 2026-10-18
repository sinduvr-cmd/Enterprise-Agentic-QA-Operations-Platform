"""
Pydantic schemas for Human-in-the-Loop Approval requests.
"""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ApprovalDecision(BaseModel):
    decision: str = Field(..., description="approved | rejected | regenerate")
    reviewer_comment: Optional[str] = None
    edited_content: Optional[Dict[str, Any]] = None


class ApprovalRequestOut(BaseModel):
    id: str
    project_id: str
    workflow_id: str
    artifact_type: str
    artifact_id: Optional[str] = None
    artifact_summary: Optional[str] = None
    quality_score: float
    status: str
    reviewer_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    reviewer_comment: Optional[str] = None
    decision_timestamp: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
