"""
AgentRun and WorkflowCheckpoint models for LangGraph orchestration and checkpoint persistence.
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(100), unique=True, index=True, nullable=False)
    project_id = Column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_id = Column(String(36), ForeignKey("requirements.id", ondelete="SET NULL"), nullable=True, index=True)
    run_name = Column(String(255), nullable=False)
    current_stage = Column(String(100), default="requirement_analysis", nullable=False)
    # Stages: requirement_analysis | test_case_generation | critic_evaluation | human_test_approval |
    #         automation_generation | automation_review | human_code_approval | git_pr_dispatch |
    #         ci_execution | failure_analysis | completed | failed | paused
    status = Column(String(50), default="running", nullable=False)  # running | awaiting_approval | completed | failed | paused
    quality_score = Column(Float, default=0.0, nullable=False)
    critic_attempts = Column(Integer, default=0, nullable=False)
    max_critic_attempts = Column(Integer, default=5, nullable=False)
    agent_reasoning_log = Column(JSON, default=list, nullable=False)  # [{timestamp, agent, thought, action, result}]
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="agent_runs")
    requirement = relationship("Requirement", back_populates="agent_runs")
    checkpoints = relationship("WorkflowCheckpoint", back_populates="agent_run", cascade="all, delete-orphan")
    evaluations = relationship("QualityEvaluation", back_populates="agent_run", cascade="all, delete-orphan")
    approvals = relationship("ApprovalRequest", back_populates="agent_run", cascade="all, delete-orphan")
    ci_execution = relationship("CIExecution", uselist=False, back_populates="agent_run")


class WorkflowCheckpoint(Base):
    __tablename__ = "workflow_checkpoints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(100), ForeignKey("agent_runs.workflow_id", ondelete="CASCADE"), nullable=False, index=True)
    step_name = Column(String(100), nullable=False)
    state_payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    agent_run = relationship("AgentRun", back_populates="checkpoints")
