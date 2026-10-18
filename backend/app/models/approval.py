"""
ApprovalRequest model for Human-in-the-Loop gates.
Enforces that generated test cases and automation code cannot proceed without human signoff.
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_id = Column(String(100), ForeignKey("agent_runs.workflow_id", ondelete="CASCADE"), nullable=False, index=True)
    artifact_type = Column(String(50), nullable=False)  # test_cases | automation_code | pr_dispatch
    artifact_id = Column(String(100), nullable=True)  # reference to test_case_id or script_id
    artifact_summary = Column(Text, nullable=True)
    quality_score = Column(Float, default=0.0, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending | approved | rejected | regenerated
    reviewer_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewer_name = Column(String(255), nullable=True)
    reviewer_comment = Column(Text, nullable=True)
    reviewer_changes = Column(JSON, default=dict, nullable=False)
    decision_timestamp = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="approval_requests")
    agent_run = relationship("AgentRun", back_populates="approvals")
    reviewer = relationship("User", back_populates="approvals")
