"""
Requirement models for user stories, acceptance criteria, and extracted testable scenarios.
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    req_uid = Column(String(50), nullable=False, index=True)  # e.g. REQ-PAY-001
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    source = Column(String(50), default="manual", nullable=False)  # manual | github_issue | jira
    github_issue_url = Column(String(512), nullable=True)
    github_issue_number = Column(String(50), nullable=True)
    acceptance_criteria = Column(JSON, default=list, nullable=False)  # list of criteria strings
    extracted_scenarios = Column(JSON, default=list, nullable=False)  # positive, negative, boundary scenarios from Agent 1
    ambiguities = Column(JSON, default=list, nullable=False)  # flagged missing information or ambiguities
    status = Column(String(50), default="draft", nullable=False)  # draft | analyzed | test_cases_generated | approved
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="requirements")
    test_cases = relationship("TestCase", back_populates="requirement", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="requirement")
