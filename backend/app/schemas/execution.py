"""
Pydantic schemas for CI Executions, Test Results, and Failure Analyses.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class FailureAnalysisOut(BaseModel):
    id: str
    root_cause_category: str
    confidence_score: float
    explanation: str
    suggested_fix: str
    evidence: List[Any] = []
    analyzed_at: datetime

    model_config = {"from_attributes": True}


class TestResultOut(BaseModel):
    id: str
    test_name: str
    status: str
    duration_ms: int
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    screenshot_url: Optional[str] = None
    trace_url: Optional[str] = None
    created_at: datetime
    failure_analysis: Optional[FailureAnalysisOut] = None

    model_config = {"from_attributes": True}


class CIExecutionOut(BaseModel):
    id: str
    project_id: str
    workflow_id: Optional[str] = None
    run_number: int
    branch: str
    commit_sha: Optional[str] = None
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    status: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    duration_seconds: float
    trigger_type: str
    artifacts_url: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CIExecutionDetail(CIExecutionOut):
    raw_logs: Optional[str] = None
    test_results: List[TestResultOut] = []
