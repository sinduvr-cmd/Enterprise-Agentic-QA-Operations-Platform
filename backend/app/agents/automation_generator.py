"""
Agent 4: Automation Generator Agent.
Synthesizes enterprise-grade Python Playwright/Pytest test automation scripts based on approved test cases.
Enforces:
- Page Object Model (POM) pattern
- Resilient locators (data-testid, role, text; avoiding brittle absolute xpaths)
- Native Playwright web-first assertions (expect(locator).to_be_visible(), etc.)
- Zero unnecessary fixed waits (no time.sleep)
- Modular fixtures (conftest.py, browser contexts, isolated test environments)
"""
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from backend.app.models.test_case import TestCase
from backend.app.agents.llm_client import llm_client


class GeneratedAutomationCode(BaseModel):
    file_path: str = Field(..., description="e.g. tests/e2e/test_checkout_flow.py")
    class_name: str = Field(..., description="e.g. TestCheckoutFlow")
    test_code: str = Field(..., description="Complete executable pytest-playwright test code")
    page_objects: Dict[str, str] = Field(default_factory=dict, description="Filename to Page Object class code")
    fixtures: Dict[str, str] = Field(default_factory=dict, description="e.g. conftest.py content")
    framework: str = "playwright-python"
    test_runner: str = "pytest"
    reasoning_summary: str


class AutomationGeneratorAgent:
    """
    Agent 4 in the QA Operations Platform.
    Converts approved structured test cases into Page Object Model automation suites.
    """

    SYSTEM_PROMPT = """You are a Principal Test Automation Architect specializing in Python Playwright and Pytest.
Your mission is to generate clean, maintainable, production-ready test automation scripts based on approved test cases.

Key Engineering Standards:
1. Apply the Page Object Model (POM):
   - Page classes encapsulate locators and user interactions.
   - Test classes focus strictly on business intent and assertions.
2. Locator Strategy:
   - Prioritize user-facing locators: `page.get_by_role()`, `page.get_by_test_id()`, `page.get_by_label()`, `page.get_by_text()`.
   - Never generate brittle absolute XPaths like `/html/body/div[1]/...` or unstable CSS classes.
3. Assertions:
   - Use Playwright's web-first assertions: `expect(locator).to_be_visible()`, `expect(locator).to_have_text(...)`.
   - NEVER use fixed sleep timers (`time.sleep()`).
4. Reusable Fixtures:
   - Generate `conftest.py` with base_url, authenticated page fixtures, and test data clean-up.
5. Structure:
   - Output valid Python code with clean type hints, docstrings, and pytest markers (`@pytest.mark.critical`, etc.).
"""

    def generate_script(
        self,
        test_case: TestCase,
        project_name: str = "Enterprise Service",
        base_url: str = "https://staging.example.com"
    ) -> GeneratedAutomationCode:
        # Normalize file and class names
        clean_slug = re.sub(r"[^a-zA-Z0-9]+", "_", test_case.test_uid.lower()).strip("_")
        clean_class = "".join(part.capitalize() for part in clean_slug.split("_"))
        file_path = f"tests/e2e/test_{clean_slug}.py"

        user_prompt = f"""Test Case UID: {test_case.test_uid}
Title: {test_case.title}
Objective: {test_case.objective}
Preconditions:
{test_case.preconditions}

Steps:
{test_case.steps}

Test Data:
{test_case.test_data}

Expected Results:
{test_case.expected_results}

Project: {project_name}
Target Base URL: {base_url}

Generate the Page Object classes, fixtures, and Playwright Pytest test suite."""

        def mock_generator() -> GeneratedAutomationCode:
            page_class_name = f"{clean_class}Page"

            page_object_code = f'''from playwright.sync_api import Page, Locator, expect

class {page_class_name}:
    """Page Object encapsulating UI interactions for {test_case.title}."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        # Resilient locators prioritizing test IDs and accessible roles
        self.primary_input = page.get_by_test_id("primary-input")
        self.submit_btn = page.get_by_role("button", name="Submit")
        self.confirmation_toast = page.get_by_test_id("confirmation-status")
        self.error_banner = page.get_by_test_id("error-banner")

    def navigate(self):
        """Navigate to the target feature endpoint."""
        self.page.goto(self.base_url)
        expect(self.page).to_have_title(re.compile(r".*"))

    def fill_and_submit(self, input_val: str):
        """Enter value and submit."""
        self.primary_input.fill(input_val)
        self.submit_btn.click()

    def get_status_text(self) -> str:
        """Returns confirmation text after auto-waiting."""
        expect(self.confirmation_toast).to_be_visible()
        return self.confirmation_toast.inner_text()
'''

            conftest_code = f'''import pytest
from playwright.sync_api import Page

@pytest.fixture(scope="session")
def base_url():
    return "{base_url}"

@pytest.fixture
def feature_page(page: Page, base_url: str):
    from pages.{clean_slug}_page import {page_class_name}
    page_obj = {page_class_name}(page, base_url)
    page_obj.navigate()
    return page_obj
'''

            test_suite_code = f'''import pytest
from playwright.sync_api import Page, expect
from pages.{clean_slug}_page import {page_class_name}

class Test{clean_class}:
    """Playwright E2E suite validating {test_case.test_uid}: {test_case.title}."""

    @pytest.mark.{test_case.priority.lower()}
    def test_{clean_slug}_execution(self, page: Page, base_url: str):
        """
        Objective: {test_case.objective}
        """
        # 1. Initialize Page Object Model
        feature_page = {page_class_name}(page, base_url)
        feature_page.navigate()

        # 2. Execute interaction using structured test data
        test_data_val = "{test_case.test_data.get('identifier', 'sample-input-val')}"
        feature_page.fill_and_submit(test_data_val)

        # 3. Assert expected outcome using auto-waiting web assertions
        expect(feature_page.confirmation_toast).to_be_visible(timeout=8000)
        expect(feature_page.error_banner).not_to_be_visible()
'''

            return GeneratedAutomationCode(
                file_path=file_path,
                class_name=f"Test{clean_class}",
                test_code=test_suite_code,
                page_objects={f"pages/{clean_slug}_page.py": page_object_code},
                fixtures={"conftest.py": conftest_code},
                framework="playwright-python",
                test_runner="pytest",
                reasoning_summary=f"Generated Page Object Model suite '{file_path}' with {page_class_name} and conftest fixtures. Web-first auto-waiting assertions applied."
            )

        return llm_client.invoke_structured(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=GeneratedAutomationCode,
            mock_fallback_fn=mock_generator
        )
