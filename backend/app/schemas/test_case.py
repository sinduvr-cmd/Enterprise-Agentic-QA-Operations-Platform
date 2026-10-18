"""
Pydantic schemas for Test Cases and Quality Evaluations.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TestStep(BaseModel):
    step: int
    action: str
    expected: str


class TestCaseBase(BaseModel):
    title: str = Field(..., max_length=255)
    objective: str
    preconditions: List[str] = []
    steps: List[Dict[str, Any]] = []
    test_data: Dict[str, Any] = {}
    expected_results: str
    priority: str = "Medium"
    category: str = "Functional"


class TestCaseCreate(TestCaseBase):
    project_id: str
    requirement_id: Optional[str] = None
    test_uid: Optional[str] = None


class TestCaseUpdate(BaseModel):
    title: Optional[str] = None
    objective: Optional[str] = None
    preconditions: Optional[List[str]] = None
    steps: Optional[List[Dict[str, Any]]] = None
    test_data: Optional[Dict[str, Any]] = None
    expected_results: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None


class TestCaseOut(TestCaseBase):
    id: str
    project_id: str
    requirement_id: Optional[str] = None
    test_uid: str
    quality_score: float
    critic_feedback: Optional[str] = None
    is_automated: bool
    status: str
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QualityEvaluationOut(BaseModel):
    id: str
    test_case_id: str
    score: float
    completeness: float
    accuracy: float
    coverage: float
    clarity: float
    traceability: float
    duplication_risk: float
    feedback: str
    attempt_number: int
    created_at: datetime

    model_config = {"from_attributes": True}
