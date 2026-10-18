"""
Unit tests for Agent 4: Automation Generator Agent.
"""
from backend.app.models.test_case import TestCase as TestCaseModel
from backend.app.agents.automation_generator import AutomationGeneratorAgent


def test_automation_generator_pom_structure():
    generator = AutomationGeneratorAgent()

    test_case = TestCaseModel(
        test_uid="TC-PAY-001",
        title="Verify successful payment confirmation flow",
        objective="Validate that checkout form completes and returns confirmation status.",
        preconditions=["User navigates to checkout", "Valid session established"],
        steps=[
            {"step": 1, "action": "Enter input details", "expected": "Validation green"},
            {"step": 2, "action": "Click submit", "expected": "Confirmation displayed"}
        ],
        test_data={"identifier": "order-val-109"},
        expected_results="Confirmation toast visible with AUTHORIZED status.",
        priority="Critical",
        category="Positive"
    )

    script_data = generator.generate_script(test_case=test_case, project_name="Core Payment Gateway")

    assert script_data.file_path.endswith(".py")
    assert "tests/e2e/test_tc_pay_001.py" in script_data.file_path
    assert "class TestTcPay001" in script_data.test_code
    assert "expect(" in script_data.test_code
    assert "time.sleep(" not in script_data.test_code

    # Verify Page Object was created
    assert len(script_data.page_objects) >= 1
    page_object_content = list(script_data.page_objects.values())[0]
    assert "class TcPay001Page:" in page_object_content
    assert "get_by_test_id" in page_object_content or "get_by_role" in page_object_content

    # Verify Fixture was created
    assert "conftest.py" in script_data.fixtures
    assert "@pytest.fixture" in script_data.fixtures["conftest.py"]
