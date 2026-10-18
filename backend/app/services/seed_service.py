"""
Realistic Enterprise Demonstration Data Seeder.
Populates projects, requirements, test cases, Playwright scripts, agent workflows, CI results, and audit trails.
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import logging

from backend.app.models.user import User
from backend.app.models.project import Project, ProjectMembership, RepositoryConfiguration
from backend.app.models.requirement import Requirement
from backend.app.models.test_case import TestCase, TestCaseVersion, QualityEvaluation
from backend.app.models.automation_script import AutomationScript
from backend.app.models.workflow import AgentRun, WorkflowCheckpoint
from backend.app.models.approval import ApprovalRequest
from backend.app.models.execution import CIExecution, TestResult, FailureAnalysis
from backend.app.models.audit import AuditLog
from backend.app.core.security import hash_password

logger = logging.getLogger(__name__)


def seed_demonstration_data(db: Session):
    # Check if already seeded
    if db.query(User).count() > 0:
        logger.info("Demonstration data already present. Skipping seeding.")
        return

    logger.info("Seeding realistic enterprise demonstration data...")
    now = datetime.now(timezone.utc)

    # 1. Users
    admin_user = User(
        email="admin@enterprise-qa.io",
        full_name="Marcus Vance (QA Director)",
        role="Admin",
        hashed_password=hash_password("admin123"),
        is_active=True,
        created_at=now - timedelta(days=60),
    )
    qa_manager = User(
        email="sarah.chen@enterprise-qa.io",
        full_name="Sarah Chen (Lead QA Architect)",
        role="QA Manager",
        hashed_password=hash_password("manager123"),
        is_active=True,
        created_at=now - timedelta(days=45),
    )
    qa_engineer = User(
        email="alex.rivera@enterprise-qa.io",
        full_name="Alex Rivera (Senior SDET)",
        role="QA Engineer",
        hashed_password=hash_password("engineer123"),
        is_active=True,
        created_at=now - timedelta(days=30),
    )
    viewer_user = User(
        email="compliance.auditor@enterprise-qa.io",
        full_name="Elena Rostova (Compliance Officer)",
        role="Viewer",
        hashed_password=hash_password("viewer123"),
        is_active=True,
        created_at=now - timedelta(days=15),
    )
    db.add_all([admin_user, qa_manager, qa_engineer, viewer_user])
    db.commit()

    # 2. Projects
    projects_data = [
        {
            "id": "proj-core-payment-gateway",
            "name": "Core Payment Gateway",
            "description": "High-throughput financial transaction processing engine supporting 3D-Secure 2.0, card tokenization, and dynamic FX routing.",
            "source_repo": "https://github.com/enterprise-org/payment-gateway-service",
            "automation_repo": "https://github.com/enterprise-org/qa-payment-playwright",
            "default_branch": "main",
            "framework_config": {
                "framework": "playwright-python",
                "test_runner": "pytest",
                "pattern": "Page Object Model",
                "base_url": "https://checkout.staging.enterprise.bank",
                "browsers": ["chromium", "firefox", "webkit"],
                "headless": True
            }
        },
        {
            "id": "proj-food-waste-manager",
            "name": "Smart Food Waste Manager",
            "description": "Smart Food Waste Management System - Streamlit web app connecting food donors with NGOs and volunteers for surplus food rescue and claim tracking.",
            "source_repo": "https://github.com/sinduvr-cmd/smart-food-waste-manager-app",
            "automation_repo": "https://github.com/sinduvr-cmd/smart-food-waste-manager-app",
            "default_branch": "main",
            "framework_config": {
                "framework": "playwright-python",
                "test_runner": "pytest",
                "pattern": "Page Object Model",
                "base_url": "http://localhost:8501",
                "browsers": ["chromium", "firefox"],
                "headless": True
            }
        },
        {
            "id": "proj-logistics-tracking",
            "name": "Global Logistics API",
            "description": "Distributed freight telematics, route optimization, and carrier webhook notification service.",
            "source_repo": "https://github.com/enterprise-org/logistics-telematics-api",
            "automation_repo": "https://github.com/enterprise-org/qa-logistics-suite",
            "default_branch": "main",
            "framework_config": {
                "framework": "playwright-python",
                "test_runner": "pytest",
                "pattern": "Page Object Model",
                "base_url": "https://telemetry.staging.freight-flow.com",
                "browsers": ["chromium"],
                "headless": True
            }
        }
    ]

    for p in projects_data:
        proj_obj = Project(
            id=p["id"],
            name=p["name"],
            description=p["description"],
            source_repo=p["source_repo"],
            automation_repo=p["automation_repo"],
            default_branch=p["default_branch"],
            framework_config=p["framework_config"],
            is_archived=False,
            created_at=now - timedelta(days=20),
            updated_at=now - timedelta(days=1),
        )
        db.add(proj_obj)

        # Memberships
        db.add(ProjectMembership(project_id=p["id"], user_id=admin_user.id, role="Admin"))
        db.add(ProjectMembership(project_id=p["id"], user_id=qa_manager.id, role="QA Manager"))
        db.add(ProjectMembership(project_id=p["id"], user_id=qa_engineer.id, role="QA Engineer"))
        db.add(ProjectMembership(project_id=p["id"], user_id=viewer_user.id, role="Viewer"))

        # Repo Config
        db.add(RepositoryConfiguration(
            project_id=p["id"],
            github_owner="enterprise-org",
            source_repo_name=p["source_repo"].split("/")[-1],
            automation_repo_name=p["automation_repo"].split("/")[-1],
            token_secret_ref="vault://secret/github/org-token",
            webhook_secret="whsec_enterprise_qa_demo_hash_98213",
        ))

    db.commit()

    # 3. Requirements
    req1 = Requirement(
        project_id="proj-core-payment-gateway",
        req_uid="REQ-PAY-101",
        title="3D-Secure 2.0 Step-Up Challenge Verification",
        description="As a cardholder, when initiating a high-risk online payment, I must complete a 3D-Secure 2.0 challenge (SMS OTP or biometric in-app push) so that unauthorized fraud is prevented.",
        source="github_issue",
        github_issue_url="https://github.com/enterprise-org/payment-gateway-service/issues/142",
        github_issue_number="142",
        acceptance_criteria=[
            "Transactions over $250 or with flagged fraud velocity must prompt 3DS2 challenge modal",
            "Successful OTP validation immediately transitions charge status to 'AUTHORIZED'",
            "Three invalid OTP entries trigger automatic decline and merchant webhook 'charge.failed'",
            "Cardholder cancellation closes modal and records user cancellation telemetry"
        ],
        extracted_scenarios=[
            {"type": "positive", "scenario": "Valid OTP submission within 120s timer authorizes charge"},
            {"type": "negative", "scenario": "Incorrect OTP entered 3 times triggers decline"},
            {"type": "boundary", "scenario": "Transaction amount exactly $250.00 threshold triggers risk engine evaluation"},
            {"type": "edge", "scenario": "Network timeout during ACS bank challenge frame displays graceful retry"}
        ],
        status="test_cases_generated",
        created_by="sarah.chen@enterprise-qa.io",
        created_at=now - timedelta(days=5),
    )

    req2 = Requirement(
        project_id="proj-food-waste-manager",
        req_uid="REQ-FWM-101",
        title="Food Donor Listing & Real-time NGO Surplus Claim Verification",
        description="As a verified NGO coordinator or volunteer, I must be able to view surplus food donations, filter by perishable expiry window and distance, and claim listings with automatic status synchronization.",
        source="manual",
        acceptance_criteria=[
            "Surplus food listings display donor location, food category, quantity in kg, and expiry timestamp.",
            "NGO coordinators can claim available food packages and generate a digital pickup authorization pass.",
            "Claimed food items instantly update state to 'Claimed' and notify donor via SMS/email webhook.",
            "Expired listings (>24h beyond perishable date) are flagged and rerouted to composting partners."
        ],
        extracted_scenarios=[
            {"type": "positive", "scenario": "NGO coordinator successfully claims available surplus listing and receives pickup pass"},
            {"type": "negative", "scenario": "Attempting to claim already claimed or expired food listing displays warning"}
        ],
        status="analyzed",
        created_by="sindu@food-rescue.org",
        created_at=now - timedelta(days=3),
    )
    db.add_all([req1, req2])
    db.commit()

    # 4. Test Cases for Payment Gateway
    tc1 = TestCase(
        project_id="proj-core-payment-gateway",
        requirement_id=req1.id,
        test_uid="TC-PAY-001",
        title="Verify successful 3DS2 OTP step-up challenge authorization",
        objective="Validate that a cardholder providing a valid SMS OTP achieves payment authorization without error.",
        preconditions=["User navigates to checkout", "Cart total is $320.00", "Enrolled 3DS2 test card loaded"],
        steps=[
            {"step": 1, "action": "Enter card details for test Visa ending in 4242", "expected": "Form fields validate green"},
            {"step": 2, "action": "Click 'Submit Payment'", "expected": "3DS2 ACS challenge iframe opens"},
            {"step": 3, "action": "Enter correct OTP code '123456'", "expected": "Challenge verifies and returns success token"},
            {"step": 4, "action": "Wait for payment confirmation screen", "expected": "Receipt displayed with Authorization Code"}
        ],
        test_data={"card": "4242-4242-4242-4242", "cvv": "123", "amount": 320.00, "otp": "123456"},
        expected_results="Transaction status is AUTHORIZED, order confirmation email dispatched, no duplicate charges.",
        priority="Critical",
        category="Positive",
        quality_score=9.4,
        critic_feedback="Comprehensive step coverage. Assertions, test data, and preconditions trace 100% to REQ-PAY-101.",
        is_automated=True,
        status="approved",
        created_at=now - timedelta(days=4),
    )

    tc2 = TestCase(
        project_id="proj-core-payment-gateway",
        requirement_id=req1.id,
        test_uid="TC-PAY-002",
        title="Verify transaction rejection after 3 invalid OTP attempts",
        objective="Ensure security enforcement blocks brute force attempts against 3DS challenge frame.",
        preconditions=["User checkout initiated with high-risk flagged card"],
        steps=[
            {"step": 1, "action": "Enter card details and submit", "expected": "3DS2 challenge displayed"},
            {"step": 2, "action": "Enter invalid OTP '000000' attempt 1", "expected": "Error message 'Invalid code, 2 tries remaining'"},
            {"step": 3, "action": "Enter invalid OTP '111111' attempt 2", "expected": "Error message 'Invalid code, 1 try remaining'"},
            {"step": 4, "action": "Enter invalid OTP '222222' attempt 3", "expected": "Challenge aborted, card declined"}
        ],
        test_data={"card": "4000-0000-0000-0002", "amount": 550.00},
        expected_results="Transaction marked as DECLINED_FRAUD_RISK. Error toast shown to user. Audit logged.",
        priority="High",
        category="Negative",
        quality_score=9.1,
        critic_feedback="Accurate boundary and negative test scenario covering brute-force lockout.",
        is_automated=True,
        status="approved",
        created_at=now - timedelta(days=4),
    )

    tc3 = TestCase(
        project_id="proj-core-payment-gateway",
        requirement_id=req1.id,
        test_uid="TC-PAY-003",
        title="Verify ACS frame timeout handling after 120 seconds",
        objective="Verify system does not hang when bank authentication server fails to respond.",
        preconditions=["Simulate 120s ACS gateway latency"],
        steps=[
            {"step": 1, "action": "Submit checkout", "expected": "Challenge iframe launched"},
            {"step": 2, "action": "Allow timer to elapse 120 seconds without input", "expected": "Timeout handler triggers"},
            {"step": 3, "action": "Verify fallback message", "expected": "'Authentication timed out. Please try again.'"}
        ],
        test_data={"timeout_ms": 120000},
        expected_results="Graceful timeout message with idempotent retry button.",
        priority="Medium",
        category="Boundary",
        quality_score=8.7,
        critic_feedback="Edge condition validated with clear recovery steps.",
        is_automated=False,
        status="pending_approval",
        created_at=now - timedelta(days=2),
    )
    db.add_all([tc1, tc2, tc3])
    db.commit()

    # 5. Playwright Automation Scripts
    script1 = AutomationScript(
        project_id="proj-core-payment-gateway",
        test_case_id=tc1.id,
        file_path="tests/e2e/test_payment_3ds.py",
        class_name="TestPayment3DSChallenge",
        test_code='''import pytest
from playwright.sync_api import Page, expect
from pages.checkout_page import CheckoutPage
from pages.challenge_modal import ChallengeModalPage

class TestPayment3DSChallenge:
    """Automated Playwright test for REQ-PAY-101 3DS2 Challenge Verification."""

    @pytest.mark.critical
    def test_payment_3ds_success(self, page: Page, base_url: str):
        checkout = CheckoutPage(page, base_url)
        challenge = ChallengeModalPage(page)

        checkout.navigate()
        checkout.fill_payment_details(
            card_number="4242424242424242",
            expiry="12/28",
            cvv="123"
        )
        checkout.submit_order()

        # Verify 3DS frame loads
        expect(challenge.challenge_frame).to_be_visible(timeout=10000)
        challenge.enter_otp("123456")
        challenge.confirm_challenge()

        # Assert confirmation screen
        expect(page.locator("[data-testid='order-confirmation']")).to_be_visible()
        expect(page.locator("[data-testid='auth-status']")).to_have_text("AUTHORIZED")
''',
        page_objects={
            "CheckoutPage": "class CheckoutPage: def __init__(self, page, base_url): self.page = page ...",
            "ChallengeModalPage": "class ChallengeModalPage: def __init__(self, page): self.challenge_frame = page.frame_locator('#acs-frame') ..."
        },
        fixtures={"conftest.py": "@pytest.fixture\ndef base_url(): return 'https://checkout.staging.enterprise.bank'"},
        review_status="approved",
        syntax_valid="valid",
        created_at=now - timedelta(days=3),
    )
    db.add(script1)
    db.commit()

    # 6. Agent Runs (Workflows)
    run1 = AgentRun(
        workflow_id="wf-pay-901",
        project_id="proj-core-payment-gateway",
        requirement_id=req1.id,
        run_name="Full QA Cycle: 3DS2 Step-Up Authentication",
        current_stage="completed",
        status="completed",
        quality_score=9.25,
        critic_attempts=2,
        max_critic_attempts=5,
        agent_reasoning_log=[
            {"timestamp": (now - timedelta(hours=5)).strftime("%H:%M:%S"), "agent": "Requirement Analyzer", "thought": "Identified 4 functional rules, 2 boundary conditions, and 1 fraud security criteria.", "action": "Extracted testable scenarios", "result": "4 scenarios formatted"},
            {"timestamp": (now - timedelta(hours=4)).strftime("%H:%M:%S"), "agent": "Test Case Generator", "thought": "Generated 3 comprehensive test cases matching POM architecture.", "action": "Synthesized test case objects", "result": "3 test cases created"},
            {"timestamp": (now - timedelta(hours=3, minutes=30)).strftime("%H:%M:%S"), "agent": "Critic Evaluator", "thought": "Attempt 1: Score 7.4. Preconditions required explicit enrolled test card credentials. Returning feedback.", "action": "Evaluated completeness", "result": "Regeneration triggered"},
            {"timestamp": (now - timedelta(hours=3)).strftime("%H:%M:%S"), "agent": "Test Case Generator", "thought": "Attempt 2: Incorporated critic guidance, added precise test card tokens and ACS frame timeout.", "action": "Updated test cases", "result": "Refined test cases"},
            {"timestamp": (now - timedelta(hours=2, minutes=45)).strftime("%H:%M:%S"), "agent": "Critic Evaluator", "thought": "Attempt 2: Score 9.25. Exceeds target threshold of 8.0. Proceeding to human approval.", "action": "Quality evaluation passed", "result": "Score 9.25 / 10"},
            {"timestamp": (now - timedelta(hours=2)).strftime("%H:%M:%S"), "agent": "Automation Generator", "thought": "Synthesized Playwright Python POM test_payment_3ds.py with custom fixtures.", "action": "Code generation", "result": "Playwright script generated"},
            {"timestamp": (now - timedelta(hours=1)).strftime("%H:%M:%S"), "agent": "CI Execution Monitor", "thought": "Executed Playwright suite in GitHub Actions headless Chromium runner.", "action": "CI test dispatch", "result": "24/24 passed"}
        ],
        started_at=now - timedelta(hours=6),
        completed_at=now - timedelta(hours=1),
    )

    run2 = AgentRun(
        workflow_id="wf-fwm-902",
        project_id="proj-food-waste-manager",
        requirement_id=req2.id,
        run_name="Agentic Sprint: Food Waste Claim & Donor Verification",
        current_stage="human_test_approval",
        status="awaiting_approval",
        quality_score=9.1,
        critic_attempts=1,
        agent_reasoning_log=[
            {"timestamp": (now - timedelta(minutes=45)).strftime("%H:%M:%S"), "agent": "Requirement Analyzer", "thought": "Analyzed Food Waste Claim & Donor Verification requirement from Streamlit app specification.", "action": "Scenarios extracted", "result": "Surplus listing and claim workflow mapped"},
            {"timestamp": (now - timedelta(minutes=30)).strftime("%H:%M:%S"), "agent": "Test Case Generator", "thought": "Synthesized 4 End-to-End Streamlit UI test scenarios for food claiming.", "action": "Generated test cases", "result": "Ready for critic"},
            {"timestamp": (now - timedelta(minutes=15)).strftime("%H:%M:%S"), "agent": "Critic Evaluator", "thought": "Quality score 9.1 / 10. Claim verification and pickup authorization meet QA criteria. Gate opened for human signoff.", "action": "Approved quality gate", "result": "Awaiting human review"}
        ],
        started_at=now - timedelta(hours=1),
    )

    run3 = AgentRun(
        workflow_id="wf-log-903",
        project_id="proj-logistics-tracking",
        run_name="Continuous Telemetry Automation Suite",
        current_stage="failure_analysis",
        status="failed",
        quality_score=8.4,
        critic_attempts=1,
        agent_reasoning_log=[
            {"timestamp": (now - timedelta(minutes=20)).strftime("%H:%M:%S"), "agent": "CI Execution Monitor", "thought": "GitHub Actions run failed on parcel tracking modal verification.", "action": "CI completed with errors", "result": "1 test failed"},
            {"timestamp": (now - timedelta(minutes=5)).strftime("%H:%M:%S"), "agent": "Failure Analysis Agent", "thought": "Inspected Playwright trace and HTML snapshot. Element locator '#track-parcel-btn' was renamed to '[data-testid=track-btn]'.", "action": "Diagnostic root cause", "result": "Classified: Locator issue"}
        ],
        started_at=now - timedelta(minutes=50),
        completed_at=now - timedelta(minutes=5),
    )

    run4 = AgentRun(
        workflow_id="wf-pay-904",
        project_id="proj-core-payment-gateway",
        requirement_id=req1.id,
        run_name="Playwright POM Automated Suite",
        current_stage="automation_generation",
        status="running",
        quality_score=9.1,
        critic_attempts=1,
        agent_reasoning_log=[
            {"timestamp": (now - timedelta(minutes=10)).strftime("%H:%M:%S"), "agent": "Automation Generator", "thought": "Synthesizing test fixtures and page object locators for payment verification.", "action": "Generating Playwright POM scripts", "result": "Generating fixtures"}
        ],
        started_at=now - timedelta(minutes=12),
    )
    db.add_all([run1, run2, run3, run4])
    db.commit()

    # 7. Checkpoints
    db.add(WorkflowCheckpoint(
        workflow_id=run1.workflow_id,
        step_name="ci_execution",
        state_payload={"run_status": "passed", "total_tests": 24, "quality_score": 9.25}
    ))
    db.add(WorkflowCheckpoint(
        workflow_id=run2.workflow_id,
        step_name="human_test_approval",
        state_payload={"awaiting_artifact": "test_cases", "score": 9.1}
    ))
    db.commit()

    # 8. Approvals
    app1 = ApprovalRequest(
        project_id="proj-food-waste-manager",
        workflow_id=run2.workflow_id,
        artifact_type="test_cases",
        artifact_id=tc3.id,
        artifact_summary="4 Food Waste Claim & Donor Verification Test Cases (Score: 9.1/10)",
        quality_score=9.1,
        status="pending",
        created_at=now - timedelta(minutes=15),
    )
    app2 = ApprovalRequest(
        project_id="proj-core-payment-gateway",
        workflow_id=run1.workflow_id,
        artifact_type="automation_code",
        artifact_id=script1.id,
        artifact_summary="Playwright POM Script for 3DS2 Challenge Flow (test_payment_3ds.py)",
        quality_score=9.4,
        status="approved",
        reviewer_id=qa_manager.id,
        reviewer_name="Sarah Chen",
        reviewer_comment="Verified Page Object Model isolation and safe assertions. Approved for GitHub PR creation.",
        decision_timestamp=now - timedelta(hours=2),
        created_at=now - timedelta(hours=3),
    )
    db.add_all([app1, app2])
    db.commit()

    # 9. CI Executions
    ci1 = CIExecution(
        project_id="proj-core-payment-gateway",
        workflow_id=run1.workflow_id,
        run_number=108,
        branch="main",
        commit_sha="a7f84c9",
        pr_number=42,
        pr_url="https://github.com/enterprise-org/qa-payment-playwright/pull/42",
        status="passed",
        total_tests=24,
        passed_tests=24,
        failed_tests=0,
        skipped_tests=0,
        duration_seconds=48.6,
        trigger_type="workflow_dispatch",
        raw_logs="=== 24 passed in 48.62s (0:00:48) ===\nPlaywright headless Chromium matrix completed cleanly.",
        started_at=now - timedelta(hours=1, minutes=50),
        completed_at=now - timedelta(hours=1),
    )

    ci2 = CIExecution(
        project_id="proj-logistics-tracking",
        workflow_id=run3.workflow_id,
        run_number=74,
        branch="main",
        commit_sha="b3e19d2",
        status="failed",
        total_tests=15,
        passed_tests=14,
        failed_tests=1,
        skipped_tests=0,
        duration_seconds=32.1,
        trigger_type="workflow_dispatch",
        raw_logs="FAILED tests/test_telemetry.py::test_parcel_lookup - playwright._impl._errors.TimeoutError: Locator '#track-parcel-btn' not found after 10000ms",
        started_at=now - timedelta(minutes=40),
        completed_at=now - timedelta(minutes=5),
    )
    db.add_all([ci1, ci2])
    db.commit()

    # 10. Test Results & Failure Analysis
    tr_fail = TestResult(
        ci_execution_id=ci2.id,
        test_name="test_parcel_lookup_realtime_status",
        status="failed",
        duration_ms=10450,
        error_message="TimeoutError: locator.click: Timeout 10000ms exceeded waiting for locator('#track-parcel-btn')",
        stack_trace="""File "tests/test_telemetry.py", line 42, in test_parcel_lookup
    page.locator("#track-parcel-btn").click()
  File "playwright/_impl/_sync_base.py", line 103, in sync_wrap
    return target(*args, **kwargs)
playwright._impl._errors.TimeoutError: Timeout 10000ms exceeded.""",
        screenshot_url="https://storage.enterprise-qa.io/artifacts/runs/74/failure_screenshot.png",
        created_at=now - timedelta(minutes=10),
    )
    db.add(tr_fail)
    db.commit()

    fa = FailureAnalysis(
        test_result_id=tr_fail.id,
        root_cause_category="locator_issue",
        confidence_score=0.94,
        explanation="The target element '#track-parcel-btn' was renamed in upstream UI pull request #119 to '[data-testid=track-btn]' as part of the design system refactor.",
        suggested_fix="Update Page Object Locator in pages/tracking_page.py from '#track-parcel-btn' to 'page.get_by_test_id(\"track-btn\")'.",
        evidence=[
            "Upstream commit diff: <button id='track-parcel-btn'> -> <button data-testid='track-btn'>",
            "DOM snapshot: Locator '#track-parcel-btn' matched 0 elements; data-testid='track-btn' matched 1 element."
        ],
        analyzed_at=now - timedelta(minutes=8),
    )
    db.add(fa)
    db.commit()

    # 11. Initial Audit Trail
    events = [
        ("PROJECT_CREATED", "Project", "proj-core-payment-gateway", {"name": "Core Payment Gateway"}, admin_user, "proj-core-payment-gateway"),
        ("REQUIREMENT_IMPORTED", "Requirement", req1.id, {"title": req1.title, "source": "github_issue"}, qa_manager, "proj-core-payment-gateway"),
        ("AGENT_RUN_STARTED", "AgentRun", run1.id, {"run_name": run1.run_name}, qa_engineer, "proj-core-payment-gateway"),
        ("TEST_APPROVED", "ApprovalRequest", app2.id, {"decision": "approved", "reviewer": "Sarah Chen"}, qa_manager, "proj-core-payment-gateway"),
        ("CI_DISPATCHED", "CIExecution", ci1.id, {"branch": "main", "tests": 24}, admin_user, "proj-core-payment-gateway"),
    ]
    for action, res_type, res_id, details, u, pid in events:
        db.add(AuditLog(
            user_id=u.id,
            user_email=u.email,
            project_id=pid,
            action=action,
            resource_type=res_type,
            resource_id=res_id,
            details=details,
            ip_address="127.0.0.1",
            created_at=now - timedelta(hours=2),
        ))
    db.commit()
    logger.info("Enterprise demonstration data seeded successfully!")
