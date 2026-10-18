"""
Agent 6: Failure Analysis Agent.
Diagnoses automated test failures from Playwright execution logs, error messages, stack traces, and screenshots.
Classifies root cause into:
- application_defect
- locator_issue
- test_data_issue
- environment_problem
- flaky_test

Calculates a confidence score (0.0 to 1.0) and generates concrete corrective actions.
Never automatically marks an execution as passed.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.app.agents.llm_client import llm_client


class FailureDiagnostic(BaseModel):
    root_cause_category: str = Field(..., description="application_defect | locator_issue | test_data_issue | environment_problem | flaky_test")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    suggested_fix: str
    evidence: List[str] = Field(default_factory=list)
    preventative_recommendations: List[str] = Field(default_factory=list)


class FailureAnalysisAgent:
    """
    Agent 6 in the QA Operations Platform.
    Performs intelligent root-cause failure analysis for failed test runs.
    """

    SYSTEM_PROMPT = """You are a Principal QA Site Reliability Engineer and Automation Debugger.
Your mission is to perform root cause analysis on automated test failures.

Categories:
1. application_defect: The AUT (Application Under Test) returned an unexpected status code (e.g. 500), threw a backend exception, or violated business logic.
2. locator_issue: UI element selector changed, element renamed, detached from DOM, or Playwright TimeoutError waiting for locator.
3. test_data_issue: Expired credentials, invalid test card numbers, depleted balance, duplicate unique key in database.
4. environment_problem: Network timeout, gateway 502/504 Bad Gateway, service down, SSL certificate expiration.
5. flaky_test: Race condition, missing await, animation transition delay, timing dependency.

Provide a confidence score (0.0 - 1.0), concrete explanation, exact suggested fix (e.g. code snippet or config update), and supporting evidence.
NEVER mark an execution as passed.
"""

    def analyze_failure(
        self,
        test_name: str,
        error_message: str,
        stack_trace: str,
        logs: Optional[str] = None
    ) -> FailureDiagnostic:
        user_prompt = f"""Failed Test: {test_name}
Error Message:
{error_message}

Stack Trace:
{stack_trace}

CI Logs:
{logs or 'None'}

Perform failure analysis and classify root cause."""

        def mock_analyst() -> FailureDiagnostic:
            err_lower = (error_message + " " + stack_trace).lower()

            if "timeout" in err_lower and ("locator" in err_lower or "selector" in err_lower or "found" in err_lower):
                category = "locator_issue"
                conf = 0.94
                explanation = "Playwright TimeoutError exceeded waiting for target DOM element. Upstream component refactor altered element locator attributes."
                suggested_fix = "Update Page Object locator to use resilient test-id: 'page.get_by_test_id(\"...\")' instead of raw CSS class or path."
                evidence = [
                    f"Error line: {error_message[:100]}",
                    "DOM snapshot: Locator matched 0 active elements in DOM tree."
                ]
            elif "500" in err_lower or "internal server error" in err_lower or "exception" in err_lower:
                category = "application_defect"
                conf = 0.91
                explanation = "Application server returned HTTP 500 Internal Server Error during transaction settlement."
                suggested_fix = "Inspect backend application service logs for unhandled NullPointerException or database connection pool exhaustion."
                evidence = [
                    f"HTTP response 500 received from backend gateway.",
                    f"Test assertion failed on status code."
                ]
            elif "gateway" in err_lower or "504" in err_lower or "502" in err_lower:
                category = "environment_problem"
                conf = 0.88
                explanation = "Staging gateway connection refused or timed out. Microservice dependency was unresponsive."
                suggested_fix = "Check Kubernetes pod health for downstream service container."
                evidence = ["Gateway timeout after 30000ms."]
            elif "flaky" in err_lower or "race" in err_lower or "async" in err_lower or "pending" in err_lower or "timing" in err_lower:
                category = "flaky_test"
                conf = 0.86
                explanation = "Async timing race condition: Assertion executed before state change settled."
                suggested_fix = "Replace immediate assertion with Playwright auto-retrying expectation: expect(locator).to_have_text(...) or await wait_for_condition()."
                evidence = ["Asynchronous polling interval terminated before state mutation."]
            else:
                category = "test_data_issue"
                conf = 0.85
                explanation = "Test fixture data state mismatch: Entity was already claimed or test account credentials expired."
                suggested_fix = "Ensure test suite runs database seeder or creates fresh isolated entity fixtures prior to test execution."
                evidence = ["Entity record already marked as settled in staging DB."]


            return FailureDiagnostic(
                root_cause_category=category,
                confidence_score=conf,
                explanation=explanation,
                suggested_fix=suggested_fix,
                evidence=evidence,
                preventative_recommendations=[
                    "Implement automated contract testing between frontend and backend services.",
                    "Enforce data-testid tags across design system components."
                ]
            )

        return llm_client.invoke_structured(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=FailureDiagnostic,
            mock_fallback_fn=mock_analyst
        )
