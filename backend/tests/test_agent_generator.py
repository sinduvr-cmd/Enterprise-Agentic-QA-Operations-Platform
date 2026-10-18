"""
Unit tests for Agent 2: Test Case Generator Agent.
"""
from backend.app.agents.requirement_analyzer import RequirementAnalyzerAgent
from backend.app.agents.test_case_generator import TestCaseGeneratorAgent


def test_test_case_generator_structured_output():
    analyzer = RequirementAnalyzerAgent()
    analysis = analyzer.analyze(
        title="Checkout Payment Processing",
        description="Process credit card transactions securely with CVV validation."
    )

    generator = TestCaseGeneratorAgent()
    # Attempt 1
    result1 = generator.generate(analysis=analysis, requirement_uid="REQ-PAY-001", attempt_number=1)

    assert result1.total_generated >= 4
    for tc in result1.test_cases:
        assert tc.test_uid.startswith("TC-REQ-PAY-001")
        assert len(tc.steps) >= 1
        assert len(tc.preconditions) >= 1
        assert tc.expected_results is not None
        assert tc.priority in ("Critical", "High", "Medium", "Low")
        assert tc.category in ("Positive", "Negative", "Boundary", "Edge", "Security")

    # Attempt 2 with Critic Feedback
    critic_feedback = "Include explicit test card credentials and enrolled token."
    result2 = generator.generate(
        analysis=analysis,
        requirement_uid="REQ-PAY-001",
        critic_feedback=critic_feedback,
        attempt_number=2
    )
    assert result2.total_generated >= 4
    pos_tc = next((t for t in result2.test_cases if t.category == "Positive"), None)
    assert pos_tc is not None
    # Preconditions should be enriched with critic guidance
    assert any("4242" in p for p in pos_tc.preconditions)
