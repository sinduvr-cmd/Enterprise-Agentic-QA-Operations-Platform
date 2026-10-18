"""
CIExecution, TestResult, and FailureAnalysis models.
Stores authoritative CI outcomes and AI-assisted root-cause failure diagnostics.
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class CIExecution(Base):
    __tablename__ = "ci_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_id = Column(String(100), ForeignKey("agent_runs.workflow_id", ondelete="SET NULL"), nullable=True, index=True)
    run_number = Column(Integer, default=1, nullable=False)
    branch = Column(String(255), default="main", nullable=False)
    commit_sha = Column(String(64), nullable=True)
    pr_number = Column(Integer, nullable=True)
    pr_url = Column(String(512), nullable=True)
    status = Column(String(50), default="running", nullable=False)  # queued | running | passed | failed | cancelled
    total_tests = Column(Integer, default=0, nullable=False)
    passed_tests = Column(Integer, default=0, nullable=False)
    failed_tests = Column(Integer, default=0, nullable=False)
    skipped_tests = Column(Integer, default=0, nullable=False)
    duration_seconds = Column(Float, default=0.0, nullable=False)
    trigger_type = Column(String(50), default="workflow_dispatch", nullable=False)  # workflow_dispatch | pr_merge | scheduled | manual
    raw_logs = Column(Text, nullable=True)
    artifacts_url = Column(String(512), nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="ci_executions")
    agent_run = relationship("AgentRun", back_populates="ci_execution")
    test_results = relationship("TestResult", back_populates="ci_execution", cascade="all, delete-orphan")


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ci_execution_id = Column(String(36), ForeignKey("ci_executions.id", ondelete="CASCADE"), nullable=False, index=True)
    test_case_id = Column(String(36), ForeignKey("test_cases.id", ondelete="SET NULL"), nullable=True, index=True)
    test_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # passed | failed | skipped | error
    duration_ms = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    screenshot_url = Column(String(512), nullable=True)
    trace_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    ci_execution = relationship("CIExecution", back_populates="test_results")
    test_case = relationship("TestCase", back_populates="test_results")
    failure_analysis = relationship("FailureAnalysis", uselist=False, back_populates="test_result", cascade="all, delete-orphan")


class FailureAnalysis(Base):
    __tablename__ = "failure_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_result_id = Column(String(36), ForeignKey("test_results.id", ondelete="CASCADE"), unique=True, nullable=False)
    root_cause_category = Column(String(100), nullable=False)
    # Categories: application_defect | locator_issue | test_data_issue | environment_problem | flaky_test
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0 (e.g. 0.94)
    explanation = Column(Text, nullable=False)
    suggested_fix = Column(Text, nullable=False)
    evidence = Column(JSON, default=list, nullable=False)  # log line snippets, locator mismatches
    analyzed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    test_result = relationship("TestResult", back_populates="failure_analysis")
