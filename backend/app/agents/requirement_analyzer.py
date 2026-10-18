"""
Agent 1: Requirement Analyzer Agent.
Analyzes user stories, acceptance criteria, extracts testable scenarios (positive, negative, boundary, edge),
identifies ambiguities and missing information, and determines sufficiency.
"""
from typing import List, Optional
from backend.app.agents.schemas import (
    RequirementAnalysisResult,
    TestableScenario,
    AmbiguityItem,
)
from backend.app.agents.llm_client import llm_client


class RequirementAnalyzerAgent:
    """
    Agent 1 in the QA Operations Platform.
    Decomposes raw user stories and acceptance criteria into structured testable specifications.
    """

    SYSTEM_PROMPT = """You are an Enterprise QA Automation Architect and Requirement Analyst.
Your goal is to thoroughly analyze software user stories and acceptance criteria.
Responsibilities:
1. Identify all explicit and implicit functional requirements.
2. Identify non-functional requirements (security, latency, reliability, concurrency).
3. Decompose into concrete testable scenarios:
   - Positive / Happy path
   - Negative / Error handling
   - Boundary value conditions
   - Edge / Race conditions
4. Detect ambiguities, vague terms (e.g. "fast", "reasonable"), or missing specifications.
5. Calculate a requirement sufficiency score from 1 to 10.
If the score is below 6.0, flag as insufficient for automated generation.
"""

    def analyze(
        self,
        title: str,
        description: str,
        acceptance_criteria: Optional[List[str]] = None
    ) -> RequirementAnalysisResult:
        criteria_list = acceptance_criteria or []
        criteria_text = "\n".join(f"- {c}" for c in criteria_list) if criteria_list else "None explicitly provided."

        user_prompt = f"""Requirement Title: {title}
Description:
{description}

Acceptance Criteria:
{criteria_text}

Analyze this requirement and output the structured JSON analysis."""

        def mock_analyzer() -> RequirementAnalysisResult:
            # Deterministic domain-aware analysis engine
            positives = [
                TestableScenario(
                    scenario_id="SCEN-01",
                    type="positive",
                    title=f"Verify standard happy path execution for {title}",
                    description=f"Submit valid payload and verify expected state transitions according to criteria.",
                    acceptance_criteria_ref="AC-1" if criteria_list else None
                )
            ]
            negatives = [
                TestableScenario(
                    scenario_id="SCEN-02",
                    type="negative",
                    title="Reject malformed or empty required input payload",
                    description="Submit missing or invalid tokens and verify standard 4xx error response with proper error message.",
                    acceptance_criteria_ref="AC-Error"
                )
            ]
            boundaries = [
                TestableScenario(
                    scenario_id="SCEN-03",
                    type="boundary",
                    title="Verify threshold and boundary limits",
                    description="Test min/max payload limits, string lengths, and boundary values.",
                    acceptance_criteria_ref="AC-Limit"
                )
            ]
            edges = [
                TestableScenario(
                    scenario_id="SCEN-04",
                    type="edge",
                    title="Verify network timeout and connection retry idempotency",
                    description="Simulate gateway timeout and ensure duplicate operations do not execute.",
                    acceptance_criteria_ref="AC-Idempotent"
                )
            ]

            ambiguities = []
            desc_lower = description.lower()
            if "fast" in desc_lower or "quick" in desc_lower:
                ambiguities.append(AmbiguityItem(
                    issue="Subjective performance term 'fast' used without concrete SLA (e.g. p99 < 200ms)",
                    severity="Medium",
                    clarification_question="What is the exact target latency threshold in milliseconds?"
                ))
            if not criteria_list:
                ambiguities.append(AmbiguityItem(
                    issue="No explicit acceptance criteria bullet points provided in requirement intake",
                    severity="High",
                    clarification_question="Can product management provide explicit Gherkin Given/When/Then criteria?"
                ))

            sufficiency = 8.8 if len(description) > 30 else 5.5

            return RequirementAnalysisResult(
                functional_requirements=[
                    f"Core workflow execution for '{title}'",
                    "Input validation and schema enforcement",
                    "State persistence and status transition logging"
                ],
                non_functional_requirements=[
                    "Response latency within 500ms SLA",
                    "OWASP top-10 security validation against injection",
                    "Audit event recording with user identity and timestamp"
                ],
                positive_scenarios=positives,
                negative_scenarios=negatives,
                boundary_scenarios=boundaries,
                edge_scenarios=edges,
                ambiguities=ambiguities,
                sufficiency_score=sufficiency,
                is_sufficient_for_test_generation=sufficiency >= 6.0,
                reasoning_summary=f"Requirement '{title}' successfully decomposed into 4 testable scenario categories with {len(ambiguities)} flagged ambiguity questions."
            )

        return llm_client.invoke_structured(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=RequirementAnalysisResult,
            mock_fallback_fn=mock_analyzer
        )
