"""
Pydantic schemas for Agent Workflows, Runs, and Reasoning logs.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentRunCreate(BaseModel):
    project_id: str
    requirement_id: Optional[str] = None
    run_name: Optional[str] = None
    requirement_text: Optional[str] = None
    acceptance_criteria: Optional[List[str]] = None
    target_browsers: Optional[List[str]] = ["chromium"]


class AgentReasoningStep(BaseModel):
    timestamp: str
    agent: str
    stage: str
    thought: str
    action: str
    result: Optional[str] = None


class AgentRunOut(BaseModel):
    id: str
    workflow_id: str
    project_id: str
    requirement_id: Optional[str] = None
    run_name: str
    current_stage: str
    status: str
    quality_score: float
    critic_attempts: int
    max_critic_attempts: int
    agent_reasoning_log: List[Dict[str, Any]] = []
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
