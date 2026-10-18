"""
Unit tests for Agent 3: Critic / Evaluator Agent.
"""
from backend.app.agents.requirement_analyzer import RequirementAnalyzerAgent
from backend.app.agents.test_case_generator import TestCaseGeneratorAgent
from backend.app.agents.critic_evaluator import CriticEvaluatorAgent


def test_critic_quality_scoring_loop():
    analyzer = RequirementAnalyzerAgent()
    analysis = analyzer.analyze(
        title="Biometric MFA Authentication",
        description="Verify WebAuthn fingerprint token."
    )
    generator = TestCaseGeneratorAgent()
    critic = CriticEvaluatorAgent()

    # Attempt 1: Should score below 8.0 and recommend regeneration
    suite_attempt1 = generator.generate(analysis=analysis, requirement_uid="REQ-MFA-001", attempt_number=1)
    eval_attempt1 = critic.evaluate(analysis=analysis, test_suite=suite_attempt1, attempt_number=1)

    assert eval_attempt1.overall_quality_score < 8.0
    assert eval_attempt1.is_approved_for_human_review is False
    assert eval_attempt1.recommended_action == "regenerate_with_feedback"
    assert "Attempt #1 Evaluation" in eval_attempt1.actionable_feedback

    # Attempt 2: Incorporates critic feedback and exceeds threshold (>= 8.0)
    suite_attempt2 = generator.generate(
        analysis=analysis,
        requirement_uid="REQ-MFA-001",
        critic_feedback=eval_attempt1.actionable_feedback,
        attempt_number=2
    )
    eval_attempt2 = critic.evaluate(analysis=analysis, test_suite=suite_attempt2, attempt_number=2)

    assert eval_attempt2.overall_quality_score >= 8.0
    assert eval_attempt2.is_approved_for_human_review is True
    assert eval_attempt2.recommended_action == "proceed_to_approval"
    assert len(eval_attempt2.individual_evaluations) == len(suite_attempt2.test_cases)
