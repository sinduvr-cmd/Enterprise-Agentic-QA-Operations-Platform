"""
Integration tests for the LangGraph Cyclic Agent Workflow.
Verifies the Generator-Critic refinement loop, checkpoints, and approval gate.
"""
def test_autonomous_cyclic_loop_execution(client):
    # 1. Trigger new QA run with user story
    payload = {
        "project_id": "proj-core-payment-gateway",
        "run_name": "Autonomous Sprint: 3DS2 Dynamic Routing",
        "requirement_text": "As a merchant, high-risk charges must trigger 3DS2 challenge. Valid OTP authorizes, 3 invalid OTPs decline.",
        "acceptance_criteria": [
            "Transactions over $250 prompt challenge",
            "Valid OTP gives AUTHORIZED status",
            "Invalid OTP gives DECLINED status"
        ],
        "target_browsers": ["chromium"]
    }
    res = client.post("/api/v1/workflows", json=payload, headers={"X-Demo-User-Role": "QA Engineer"})
    assert res.status_code == 201
    run_data = res.json()

    # Verify loop executed and progressed to human approval
    assert run_data["status"] == "awaiting_approval"
    assert run_data["current_stage"] == "human_test_approval"
    assert run_data["critic_attempts"] >= 2  # Ran at least 2 attempts (Attempt 1 was refined by Critic!)
    assert run_data["quality_score"] >= 8.0  # Critic score passed the 8.0 threshold!

    # 2. Verify Checkpoints persisted
    workflow_id = run_data["workflow_id"]
    cp_res = client.get(f"/api/v1/workflows/{workflow_id}/checkpoints", headers={"X-Demo-User-Role": "Viewer"})
    assert cp_res.status_code == 200
    checkpoints = cp_res.json()
    assert len(checkpoints) >= 3  # Initialized, Requirement Analysis, Test Case Gen, Critic Eval

    # 3. Verify Generated Test Cases were created in the database
    tc_res = client.get(f"/api/v1/test-cases?project_id=proj-core-payment-gateway", headers={"X-Demo-User-Role": "Viewer"})
    assert tc_res.status_code == 200
    test_cases = tc_res.json()
    assert len(test_cases) >= 4

    # 4. Verify Approval Request was queued
    app_res = client.get(f"/api/v1/approvals?project_id=proj-core-payment-gateway&status=pending", headers={"X-Demo-User-Role": "Viewer"})
    assert app_res.status_code == 200
    approvals = app_res.json()
    matching_approval = next((a for a in approvals if a["workflow_id"] == workflow_id), None)
    assert matching_approval is not None
    assert matching_approval["quality_score"] >= 8.0
    assert matching_approval["artifact_type"] == "test_cases"
