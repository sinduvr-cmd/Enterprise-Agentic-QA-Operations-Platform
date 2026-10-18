"""
Unit tests for Agent 5: Automation Reviewer Agent.
"""
from backend.app.agents.automation_generator import GeneratedAutomationCode
from backend.app.agents.automation_reviewer import AutomationReviewerAgent


def test_reviewer_approves_clean_code():
    reviewer = AutomationReviewerAgent()

    clean_code = GeneratedAutomationCode(
        file_path="tests/e2e/test_sample.py",
        class_name="TestSample",
        test_code="""from playwright.sync_api import Page, expect

def test_sample_flow(page: Page):
    page.goto("https://example.com")
    expect(page.get_by_role("button")).to_be_visible()
""",
        page_objects={"pages/sample_page.py": "class SamplePage: pass"},
        fixtures={"conftest.py": "# conftest"},
        framework="playwright-python",
        test_runner="pytest",
        reasoning_summary="Clean sample"
    )

    report = reviewer.review_code(clean_code)
    assert report.is_approved is True
    assert report.syntax_valid is True
    assert report.quality_score >= 8.5
    assert len(report.issues) == 0


def test_reviewer_detects_unsafe_code_and_secrets():
    reviewer = AutomationReviewerAgent()

    unsafe_code = GeneratedAutomationCode(
        file_path="tests/e2e/test_unsafe.py",
        class_name="TestUnsafe",
        test_code="""import os
from playwright.sync_api import Page

def test_unsafe_execution(page: Page):
    # Hardcoded credential
    api_key = "super_secret_live_token_12345"
    # Unsafe function call
    eval("2 + 2")
    # Brittle xpath
    page.locator("/html/body/div[1]/button").click()
""",
        page_objects={},
        fixtures={},
        framework="playwright-python",
        test_runner="pytest",
        reasoning_summary="Unsafe code"
    )

    report = reviewer.review_code(unsafe_code)
    assert report.is_approved is False
    assert report.quality_score < 7.0

    issue_categories = [i.category for i in report.issues]
    assert "unsafe_execution" in issue_categories
    assert "hardcoded_secret" in issue_categories
    assert "brittle_locator" in issue_categories
