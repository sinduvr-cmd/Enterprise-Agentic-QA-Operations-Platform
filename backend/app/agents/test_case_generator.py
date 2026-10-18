"""
Agent 2: Test Case Generator Agent.
Generates structured test cases with preconditions, steps, test data, expected results, priority, and requirement reference.
Iteratively incorporates Critic feedback when improving previous attempts.
"""
from typing import List, Optional, Dict, Any
from backend.app.agents.schemas import (
    RequirementAnalysisResult,
    TestCaseGenerationResult,
    GeneratedTestCase,
    GeneratedTestStep,
)
from backend.app.agents.llm_client import llm_client


class TestCaseGeneratorAgent:
    """
    Agent 2 in the QA Operations Platform.
    Synthesizes structured test suites based on scenario analysis and Critic evaluation feedback.
    """

    SYSTEM_PROMPT = """You are a Senior QA Automation Architect specializing in Enterprise Testing.
Your task is to generate complete, structured, unambiguous test cases based on analyzed requirements.

Each test case MUST include:
- test_uid: Unique string identifier (e.g. TC-PAY-001)
- title: Concise, imperative test title
- objective: What this test validates and why
- preconditions: List of required setup conditions, data, or authenticated session states
- steps: Detailed step-by-step actions with precise expected outcomes
- test_data: Explicit realistic values, tokens, or mock constants (never placeholders like 'test123')
- expected_results: Definite post-conditions and assertions
- priority: Critical | High | Medium | Low
- category: Positive | Negative | Boundary | Edge | Security
- requirement_reference: Traceability identifier

CRITICAL RULE:
If critic feedback from previous attempts is provided, you MUST address every single critique,
correcting missing preconditions, tightening assertions, expanding test data, or removing redundant steps.
"""

    def generate(
        self,
        analysis: RequirementAnalysisResult,
        requirement_uid: str = "REQ-001",
        critic_feedback: Optional[str] = None,
        attempt_number: int = 1
    ) -> TestCaseGenerationResult:
        critic_prompt_part = ""
        if critic_feedback:
            critic_prompt_part = f"""
=========================================
PREVIOUS CRITIC FEEDBACK (ATTEMPT #{attempt_number - 1}):
{critic_feedback}
You must incorporate all feedback to achieve a quality score above 8.0.
=========================================
"""

        user_prompt = f"""Requirement UID: {requirement_uid}
Functional Scope:
{json_dumps(analysis.functional_requirements)}

Positive Scenarios:
{json_dumps([s.model_dump() for s in analysis.positive_scenarios])}

Negative Scenarios:
{json_dumps([s.model_dump() for s in analysis.negative_scenarios])}

Boundary Scenarios:
{json_dumps([s.model_dump() for s in analysis.boundary_scenarios])}

Edge Scenarios:
{json_dumps([s.model_dump() for s in analysis.edge_scenarios])}
{critic_prompt_part}

Generate the comprehensive structured test case suite."""

        def mock_generator() -> TestCaseGenerationResult:
            test_cases: List[GeneratedTestCase] = []

            # 1. Positive / Happy Path Test Case
            # If attempt > 1, enrich preconditions and data in response to critic
            pos_preconds = [
                "User has valid authenticated session token",
                "Target environment is accessible and healthy",
                "Database seed test data initialized"
            ]
            if attempt_number > 1:
                pos_preconds.append("Explicit test card 4242-4242-4242-4242 enrolled in 3DS2 challenge simulator")

            tc_pos = GeneratedTestCase(
                test_uid=f"TC-{requirement_uid}-001",
                title=f"Verify successful end-to-end flow for {requirement_uid}",
                objective="Ensure valid input payload achieves successful operation with state persistence and authorization confirmation.",
                preconditions=pos_preconds,
                steps=[
                    GeneratedTestStep(step=1, action="Navigate to operational entrypoint", expected="View loads within 1000ms"),
                    GeneratedTestStep(step=2, action="Fill required input fields with valid data", expected="Client-side validation indicators highlight valid"),
                    GeneratedTestStep(step=3, action="Click 'Submit' button", expected="Processing spinner appears; payload transmitted via POST"),
                    GeneratedTestStep(step=4, action="Verify confirmation view", expected="HTTP 200 response; status displayed as AUTHORIZED with reference UUID")
                ],
                test_data={
                    "identifier": "test-entity-492",
                    "amount": 250.00,
                    "currency": "USD",
                    "auth_token": "bearer_mock_jwt_secure_token"
                },
                expected_results="Transaction record persisted in database with status 'AUTHORIZED', audit log entry recorded, confirmation payload returned.",
                priority="Critical",
                category="Positive",
                requirement_reference=requirement_uid
            )
            test_cases.append(tc_pos)

            # 2. Negative / Error Handling Test Case
            tc_neg = GeneratedTestCase(
                test_uid=f"TC-{requirement_uid}-002",
                title="Verify rejection when required fields are missing or invalid",
                objective="Ensure security validation blocks malformed requests and returns RFC-7807 compliant error details.",
                preconditions=[
                    "API gateway or web client initialized",
                    "Test user session established"
                ],
                steps=[
                    GeneratedTestStep(step=1, action="Submit request with missing mandatory fields and malformed token", expected="Form validation prevents invalid submission"),
                    GeneratedTestStep(step=2, action="Send raw API request bypassing client UI", expected="HTTP 422 Unprocessable Entity returned with specific field errors"),
                    GeneratedTestStep(step=3, action="Inspect response body schema", expected="Error JSON contains detail field listing invalid parameters")
                ],
                test_data={"invalid_payload": {"amount": -50.0, "currency": "INVALID"}},
                expected_results="Operation is rejected without state mutation. No records created. Security audit logged.",
                priority="High",
                category="Negative",
                requirement_reference=requirement_uid
            )
            test_cases.append(tc_neg)

            # 3. Boundary / Threshold Test Case
            tc_bound = GeneratedTestCase(
                test_uid=f"TC-{requirement_uid}-003",
                title="Verify boundary limits and threshold triggers",
                objective="Validate exact lower limit, upper limit, and threshold boundary transitions.",
                preconditions=[
                    "System configured with threshold rules",
                    "Test accounts created for boundary checks"
                ],
                steps=[
                    GeneratedTestStep(step=1, action="Submit value at lower boundary ($0.01)", expected="Accepted and processed"),
                    GeneratedTestStep(step=2, action="Submit value at exact threshold trigger ($250.00)", expected="Triggers step-up verification workflow"),
                    GeneratedTestStep(step=3, action="Submit value exceeding upper limit ($10,000.01)", expected="Rejected with 'Exceeds maximum allowable transaction limit'")
                ],
                test_data={"min_value": 0.01, "threshold_value": 250.00, "exceeded_value": 10000.01},
                expected_results="Boundary conditions adhere precisely to business specifications without off-by-one errors.",
                priority="Medium",
                category="Boundary",
                requirement_reference=requirement_uid
            )
            test_cases.append(tc_bound)

            # 4. Edge Case (Timeout / Idempotency)
            tc_edge = GeneratedTestCase(
                test_uid=f"TC-{requirement_uid}-004",
                title="Verify idempotent retry handling on connection drop",
                objective="Validate system prevents double-execution when network fails during transmission.",
                preconditions=["Idempotency key header configured"],
                steps=[
                    GeneratedTestStep(step=1, action="Dispatch request with Idempotency-Key: 'idem-test-991'", expected="Request processed successfully"),
                    GeneratedTestStep(step=2, action="Re-send identical request with identical idempotency key", expected="Cached response returned without duplicate execution")
                ],
                test_data={"idempotency_key": "idem-test-991", "retry_count": 2},
                expected_results="Exactly one transaction record created. Secondary request receives cached response.",
                priority="High",
                category="Edge",
                requirement_reference=requirement_uid
            )
            test_cases.append(tc_edge)

            return TestCaseGenerationResult(
                test_cases=test_cases,
                total_generated=len(test_cases),
                positive_count=1,
                negative_count=1,
                boundary_count=1,
                duplicate_candidates_removed=0,
                reasoning_summary=f"Synthesized {len(test_cases)} structured test cases across Positive, Negative, Boundary, and Edge categories for '{requirement_uid}' (Attempt #{attempt_number})."
            )

        return llm_client.invoke_structured(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=TestCaseGenerationResult,
            mock_fallback_fn=mock_generator
        )


def json_dumps(obj: Any) -> str:
    import json
    return json.dumps(obj, indent=2)
