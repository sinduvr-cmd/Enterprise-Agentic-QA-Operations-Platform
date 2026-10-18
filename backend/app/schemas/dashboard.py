"""
Pydantic schemas for Executive and Operational Dashboard data aggregation.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class DashboardSummaryCards(BaseModel):
    total_qa_runs: int
    total_qa_runs_delta: str = "+12% this week"
    running_workflows: int
    awaiting_approval: int
    passed_tests: int
    failed_tests: int
    test_cases_generated: int
    automation_coverage: float  # Percentage, e.g. 84.5
    active_projects: int


class RecentRunItem(BaseModel):
    id: str
    workflow_id: str
    project_id: str
    project_name: str
    run_name: str
    branch: str
    status: str  # running | passed | failed | awaiting_approval
    current_stage: str
    quality_score: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    duration_seconds: float
    started_at: str


class AgentTimelineItem(BaseModel):
    id: str
    timestamp: str
    agent_name: str  # Requirement Analyzer | Test Case Generator | Critic Evaluator | Automation Generator | Reviewer | Failure Analyst
    project_name: str
    workflow_id: str
    action: str
    status: str  # success | running | warning | error
    detail: str
    score: Optional[float] = None


class TrendPoint(BaseModel):
    date: str
    total_runs: int
    passed: int
    failed: int
    coverage: float


class RequirementCoveragePoint(BaseModel):
    requirement_uid: str
    title: str
    total_test_cases: int
    automated_count: int
    coverage_percent: float


class PassFailDistribution(BaseModel):
    passed: int
    failed: int
    skipped: int
    pass_rate: float


class DashboardOverviewResponse(BaseModel):
    summary: DashboardSummaryCards
    recent_runs: List[RecentRunItem]
    agent_activity: List[AgentTimelineItem]
    execution_trends: List[TrendPoint]
    pass_fail_distribution: PassFailDistribution
    requirement_coverage: List[RequirementCoveragePoint]
    pending_approvals: List[Dict[str, Any]]
    demo_mode: bool = True
