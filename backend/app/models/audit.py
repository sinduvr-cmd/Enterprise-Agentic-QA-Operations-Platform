"""
AuditLog model for enterprise governance, compliance, and traceability.
Tracks every state change, approval decision, agent regeneration, and CI execution.
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    project_id = Column(String(64), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    # Actions: PROJECT_CREATED | REQUIREMENT_IMPORTED | AGENT_RUN_STARTED | TEST_APPROVED |
    #          TEST_REJECTED | CODE_APPROVED | PR_CREATED | CI_DISPATCHED | CONFIG_UPDATED
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=False)
    details = Column(JSON, default=dict, nullable=False)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    user = relationship("User", back_populates="audit_logs")
    project = relationship("Project", back_populates="audit_logs")
