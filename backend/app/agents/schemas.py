"""
Structured Pydantic schemas for Agent inputs and outputs.
Enforces strict JSON schema validation for LLM responses.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ==========================================
# Agent 1: Requirement Analyzer Schemas
# ==========================================

class TestableScenario(BaseModel):
    scenario_id: str
    type: str = Field(..., description="positive | negative | boundary | edge | security")
    title: str
    description: str
    acceptance_criteria_ref: Optional[str] = None


class AmbiguityItem(BaseModel):
    issue: str
    severity: str = Field(default="Medium", description="Critical | High | Medium | Low")
    clarification_question: str


class RequirementAnalysisResult(BaseModel):
    functional_requirements: List[str] = Field(default_factory=list)
    non_functional_requirements: List[str] = Field(default_factory=list)
    positive_scenarios: List[TestableScenario] = Field(default_factory=list)
    negative_scenarios: List[TestableScenario] = Field(default_factory=list)
    boundary_scenarios: List[TestableScenario] = Field(default_factory=list)
    edge_scenarios: List[TestableScenario] = Field(default_factory=list)
    ambiguities: List[AmbiguityItem] = Field(default_factory=list)
    sufficiency_score: float = Field(..., ge=0.0, le=10.0, description="1-10 rating of requirement completeness")
    is_sufficient_for_test_generation: bool = True
    reasoning_summary: str


# ==========================================
# Agent 2: Test Case Generator Schemas
# ==========================================

class GeneratedTestStep(BaseModel):
    step: int
    action: str
    expected: str


class GeneratedTestCase(BaseModel):
    test_uid: str
    title: str
    objective: str
    preconditions: List[str] = Field(default_factory=list)
    steps: List[GeneratedTestStep] = Field(default_factory=list)
    test_data: Dict[str, Any] = Field(default_factory=dict)
    expected_results: str
    priority: str = Field(default="Medium", description="Critical | High | Medium | Low")
    category: str = Field(default="Functional", description="Positive | Negative | Boundary | Edge | Security")
    requirement_reference: str


class TestCaseGenerationResult(BaseModel):
    test_cases: List[GeneratedTestCase] = Field(default_factory=list)
    total_generated: int
    positive_count: int
    negative_count: int
    boundary_count: int
    duplicate_candidates_removed: int = 0
    reasoning_summary: str


# ==========================================
# Agent 3: Critic / Evaluator Schemas
# ==========================================

class TestCaseEvaluation(BaseModel):
    test_uid: str
    score: float = Field(..., ge=1.0, le=10.0)
    completeness: float = Field(..., ge=1.0, le=10.0)
    accuracy: float = Field(..., ge=1.0, le=10.0)
    coverage: float = Field(..., ge=1.0, le=10.0)
    clarity: float = Field(..., ge=1.0, le=10.0)
    traceability: float = Field(..., ge=1.0, le=10.0)
    duplication_risk: float = Field(..., ge=0.0, le=10.0, description="0=No duplication, 10=Exact duplicate")
    feedback: str
    specific_improvements: List[str] = Field(default_factory=list)


class CriticEvaluationResult(BaseModel):
    overall_quality_score: float = Field(..., ge=1.0, le=10.0)
    pass_threshold: float = 8.0
    is_approved_for_human_review: bool
    attempt_number: int
    max_attempts: int = 5
    actionable_feedback: str
    individual_evaluations: List[TestCaseEvaluation] = Field(default_factory=list)
    recommended_action: str = Field(..., description="proceed_to_approval | regenerate_with_feedback | flag_for_human_review")
    dimension_scores: Dict[str, float] = Field(default_factory=dict)
