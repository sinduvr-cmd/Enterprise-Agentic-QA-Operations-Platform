"""
TestCase, TestCaseVersion, and QualityEvaluation models.
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class TestCase(Base):
    __tablename__ = "test_cases"
    __test__ = False

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_id = Column(String(36), ForeignKey("requirements.id", ondelete="SET NULL"), nullable=True, index=True)
    test_uid = Column(String(50), nullable=False, index=True)  # e.g. TC-PAY-001
    title = Column(String(255), nullable=False)
    objective = Column(Text, nullable=False)
    preconditions = Column(JSON, default=list, nullable=False)
    steps = Column(JSON, default=list, nullable=False)  # [{step: 1, action: "...", expected: "..."}]
    test_data = Column(JSON, default=dict, nullable=False)
    expected_results = Column(Text, nullable=False)
    priority = Column(String(20), default="Medium", nullable=False)  # Critical | High | Medium | Low
    category = Column(String(50), default="Functional", nullable=False)  # Functional | Positive | Negative | Boundary | Security
    quality_score = Column(Float, default=0.0, nullable=False)  # 1.0 to 10.0 from Critic Agent
    critic_feedback = Column(Text, nullable=True)
    is_automated = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="generated", nullable=False)  # generated | critic_reviewing | pending_approval | approved | rejected
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="test_cases")
    requirement = relationship("Requirement", back_populates="test_cases")
    versions = relationship("TestCaseVersion", back_populates="test_case", cascade="all, delete-orphan")
    automation_script = relationship("AutomationScript", uselist=False, back_populates="test_case")
    evaluations = relationship("QualityEvaluation", back_populates="test_case", cascade="all, delete-orphan")
    test_results = relationship("TestResult", back_populates="test_case")


class TestCaseVersion(Base):
    __tablename__ = "test_case_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_case_id = Column(String(36), ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    snapshot = Column(JSON, nullable=False)
    diff_summary = Column(Text, nullable=True)
    critic_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    test_case = relationship("TestCase", back_populates="versions")


class QualityEvaluation(Base):
    __tablename__ = "quality_evaluations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_run_id = Column(String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=True, index=True)
    test_case_id = Column(String(36), ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)  # 1.0 to 10.0
    completeness = Column(Float, default=0.0, nullable=False)
    accuracy = Column(Float, default=0.0, nullable=False)
    coverage = Column(Float, default=0.0, nullable=False)
    clarity = Column(Float, default=0.0, nullable=False)
    traceability = Column(Float, default=0.0, nullable=False)
    duplication_risk = Column(Float, default=0.0, nullable=False)
    feedback = Column(Text, nullable=False)
    attempt_number = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    test_case = relationship("TestCase", back_populates="evaluations")
    agent_run = relationship("AgentRun", back_populates="evaluations")
