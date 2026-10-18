"""
Project, Membership, and Repository Configuration models.
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(64), primary_key=True)  # unique string ID like 'proj-payment-gateway'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_repo = Column(String(512), nullable=False)
    automation_repo = Column(String(512), nullable=False)
    default_branch = Column(String(100), default="main", nullable=False)
    framework_config = Column(JSON, default=lambda: {
        "framework": "playwright-python",
        "test_runner": "pytest",
        "pattern": "Page Object Model",
        "base_url": "https://staging.example.com",
        "browsers": ["chromium", "firefox", "webkit"],
        "headless": True
    }, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    memberships = relationship("ProjectMembership", back_populates="project", cascade="all, delete-orphan")
    repo_config = relationship("RepositoryConfiguration", uselist=False, back_populates="project", cascade="all, delete-orphan")
    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="project", cascade="all, delete-orphan")
    automation_scripts = relationship("AutomationScript", back_populates="project", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="project", cascade="all, delete-orphan")
    approval_requests = relationship("ApprovalRequest", back_populates="project", cascade="all, delete-orphan")
    ci_executions = relationship("CIExecution", back_populates="project", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="project")


class ProjectMembership(Base):
    __tablename__ = "project_memberships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), default="QA Engineer", nullable=False)  # Admin | QA Manager | QA Engineer | Viewer
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="memberships")
    user = relationship("User", back_populates="memberships")


class RepositoryConfiguration(Base):
    __tablename__ = "repository_configurations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False)
    github_owner = Column(String(255), nullable=False)
    source_repo_name = Column(String(255), nullable=False)
    automation_repo_name = Column(String(255), nullable=False)
    token_secret_ref = Column(String(255), nullable=True)  # Secure vault reference, never plain token in logs
    webhook_secret = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="repo_config")
