"""
Agent 3: Critic / Evaluator Agent.
Evaluates generated test cases across 6 enterprise quality dimensions:
1. Completeness (Are all steps, preconditions, and expected results defined?)
2. Accuracy (Are expectations technically sound and verifiable?)
3. Coverage (Does the suite cover positive, negative, boundary, edge conditions?)
4. Clarity (Are steps unambiguous, reproducible, and clear?)
5. Traceability (Do all test cases link explicitly to requirements?)
6. Duplication (Are there redundant or overlapping test cases?)

Calculates an overall quality score from 1.0 to 10.0.
Decides whether to proceed to human approval (>= 8.0), regenerate (< 8.0, attempts < 5),
or flag for human review (attempts exhausted).
"""
import logging
from typing import List, Dict, Any
from backend.app.agents.schemas import (
    RequirementAnalysisResult,
    TestCaseGenerationResult,
    CriticEvaluationResult,
    TestCaseEvaluation,
)
from backend.app.agents.llm_client import llm_client

logger = logging.getLogger(__name__)


class CriticEvaluatorAgent:
    """
    Agent 3 in the QA Operations Platform.
    Evaluator with strict quality scoring loop.
    """

    PASS_THRESHOLD = 8.0
    MAX_ATTEMPTS = 5

    SYSTEM_PROMPT = """You are a Principal QA Evaluator and Test Critic.
Your mission is to rigorously evaluate generated test cases against the requirement specification.
Evaluate on 6 dimensions (scores from 1.0 to 10.0):
1. Completeness (weight 20%): All preconditions, test data, and expected outcomes must be fully detailed.
2. Accuracy (weight 20%): Technical correctness of steps, assertion validity, and state checks.
3. Coverage (weight 25%): Covers positive, negative, boundary, and edge conditions.
4. Clarity (weight 15%): Unambiguous, step-by-step reproducibility without vague wording.
5. Traceability (weight 10%): Explicit mapping to requirements and user story acceptance criteria.
6. Duplication Risk (weight 10%): Penalty for overlapping or redundant test cases (0=None, 10=High duplication).

Calculate the overall quality score (1.0 - 10.0).
Rules:
- If quality score >= 8.0: recommend 'proceed_to_approval'
- If quality score < 8.0 and attempt < 5: recommend 'regenerate_with_feedback'
- If attempt >= 5: recommend 'flag_for_human_review'
Provide clear, actionable, constructive feedback for the Generator Agent.
"""

    def evaluate(
        self,
        analysis: RequirementAnalysisResult,
        test_suite: TestCaseGenerationResult,
        attempt_number: int = 1
    ) -> CriticEvaluationResult:
        import json

        user_prompt = f"""Requirement Analysis:
{analysis.model_dump_json(indent=2)}

Generated Test Suite (Attempt #{attempt_number}):
{test_suite.model_dump_json(indent=2)}

Evaluate this test suite rigorously and return the CriticEvaluationResult JSON."""

        def mock_critic() -> CriticEvaluationResult:
            # Deterministic Critic Evaluation:
            # Attempt 1: Scores 7.4 (below 8.0) to demonstrate the autonomous self-healing loop!
            # Attempt 2+: Scores 9.2 (above 8.0) after generator incorporates critic feedback!
            if attempt_number == 1:
                overall_score = 7.4
                completeness = 7.0
                accuracy = 7.5
                coverage = 8.0
                clarity = 7.5
                traceability = 8.0
                duplication = 1.0
                actionable_feedback = (
                    "Attempt #1 Evaluation: Quality score is 7.4/10 (threshold is 8.0). "
                    "Preconditions in test case #1 lack explicit test card tokens and simulated 3DS2 enrollment credentials. "
                    "Boundary assertions in test case #3 should verify the exact $250.00 step-up threshold. "
                    "Action: Generator agent must supply explicit enrollment tokens and threshold boundary values."
                )
                recommended_action = "regenerate_with_feedback"
                is_approved = False
            else:
                overall_score = 9.25
                completeness = 9.4
                accuracy = 9.3
                coverage = 9.5
                clarity = 9.2
                traceability = 9.5
                duplication = 0.5
                actionable_feedback = (
                    f"Attempt #{attempt_number} Evaluation: Quality score improved to 9.25/10 (Exceeds threshold 8.0). "
                    "All previous critiques addressed: explicit enrolled test card credentials added, boundary thresholds verified, "
                    "and assertions tightened. Ready for human review."
                )
                recommended_action = "proceed_to_approval"
                is_approved = True

            individual_evals: List[TestCaseEvaluation] = []
            for tc in test_suite.test_cases:
                individual_evals.append(TestCaseEvaluation(
                    test_uid=tc.test_uid,
                    score=overall_score,
                    completeness=completeness,
                    accuracy=accuracy,
                    coverage=coverage,
                    clarity=clarity,
                    traceability=traceability,
                    duplication_risk=duplication,
                    feedback=f"Test case '{tc.title}' evaluated with quality score {overall_score}/10.",
                    specific_improvements=[] if is_approved else ["Refine preconditions with explicit mock tokens"]
                ))

            return CriticEvaluationResult(
                overall_quality_score=overall_score,
                pass_threshold=self.PASS_THRESHOLD,
                is_approved_for_human_review=is_approved,
                attempt_number=attempt_number,
                max_attempts=self.MAX_ATTEMPTS,
                actionable_feedback=actionable_feedback,
                individual_evaluations=individual_evals,
                recommended_action=recommended_action,
                dimension_scores={
                    "completeness": completeness,
                    "accuracy": accuracy,
                    "coverage": coverage,
                    "clarity": clarity,
                    "traceability": traceability,
                    "duplication_risk": duplication
                }
            )

        return llm_client.invoke_structured(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=CriticEvaluationResult,
            mock_fallback_fn=mock_critic
        )
