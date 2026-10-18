"""
AutomationScript model for generated Playwright/Pytest test automation scripts.
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class AutomationScript(Base):
    __tablename__ = "automation_scripts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    test_case_id = Column(String(36), ForeignKey("test_cases.id", ondelete="CASCADE"), unique=True, nullable=False)
    file_path = Column(String(512), nullable=False)  # e.g. tests/test_payment_gateway.py
    class_name = Column(String(255), nullable=True)
    test_code = Column(Text, nullable=False)
    page_objects = Column(JSON, default=dict, nullable=False)  # {"LoginPage": "...", "CheckoutPage": "..."}
    fixtures = Column(JSON, default=dict, nullable=False)  # {"conftest.py": "..."}
    language = Column(String(50), default="python", nullable=False)
    framework = Column(String(50), default="playwright", nullable=False)
    review_status = Column(String(50), default="pending_review", nullable=False)  # pending_review | approved | changes_requested
    reviewer_notes = Column(Text, nullable=True)
    syntax_valid = Column(String(10), default="valid", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="automation_scripts")
    test_case = relationship("TestCase", back_populates="automation_script")
