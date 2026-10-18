"""
Central API v1 Router.
"""
from fastapi import APIRouter

from backend.app.api.endpoints import (
    auth,
    projects,
    dashboard,
    requirements,
    test_cases,
    automation,
    github,
    workflows,
    approvals,
    executions,
    audit,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Users"])
api_router.include_router(projects.router, prefix="/projects", tags=["Multi-Project Management"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Operations Dashboard"])
api_router.include_router(requirements.router, prefix="/requirements", tags=["Requirements & User Stories"])
api_router.include_router(test_cases.router, prefix="/test-cases", tags=["Generated Test Cases"])
api_router.include_router(automation.router, prefix="/automation", tags=["Playwright Automation Scripts"])
api_router.include_router(github.router, prefix="/github", tags=["GitHub Integration"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["Agentic Workflows & Runs"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["Human-in-the-Loop Approvals"])
api_router.include_router(executions.router, prefix="/executions", tags=["CI Executions & Results"])
api_router.include_router(audit.router, prefix="/audit", tags=["Compliance & Audit Logs"])
