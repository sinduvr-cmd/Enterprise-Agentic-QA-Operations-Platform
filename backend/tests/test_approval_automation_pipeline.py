"""
Integration tests for Phase 3: Human-in-the-Loop Approval & Automation Code Synthesis Pipeline.
"""
def test_test_case_approval_triggers_automation_code_generation(client):
    # 1. Trigger a workflow to generate test cases
    payload = {
        "project_id": "proj-core-payment-gateway",
        "run_name": "Phase 3 Pipeline Verification",
        "requirement_text": "Verify card payment processing with 3DS2 challenge step-up.",
        "acceptance_criteria": ["Transactions over $250 prompt challenge", "Valid OTP authorizes"]
    }
    wf_res = client.post("/api/v1/workflows", json=payload, headers={"X-Demo-User-Role": "QA Engineer"})
    assert wf_res.status_code == 201
    run = wf_res.json()
    workflow_id = run["workflow_id"]
    assert run["status"] == "awaiting_approval"

    # 2. Find the pending test_cases approval request
    app_res = client.get(f"/api/v1/approvals?project_id=proj-core-payment-gateway&status=pending", headers={"X-Demo-User-Role": "Viewer"})
    assert app_res.status_code == 200
    approvals = app_res.json()
    test_approval = next((a for a in approvals if a["workflow_id"] == workflow_id and a["artifact_type"] == "test_cases"), None)
    assert test_approval is not None

    # 3. QA Manager approves the test cases
    decision_payload = {
        "decision": "approved",
        "reviewer_comment": "Approved test cases for automated script generation."
    }
    dec_res = client.post(
        f"/api/v1/approvals/{test_approval['id']}/decision",
        json=decision_payload,
        headers={"X-Demo-User-Role": "QA Manager"}
    )
    assert dec_res.status_code == 200
    assert dec_res.json()["status"] == "approved"

    # 4. Verify that Agent 4 & Agent 5 automatically generated the Playwright script!
    scripts_res = client.get(f"/api/v1/automation/scripts?project_id=proj-core-payment-gateway", headers={"X-Demo-User-Role": "Viewer"})
    assert scripts_res.status_code == 200
    scripts = scripts_res.json()
    assert len(scripts) >= 1
    newest_script = scripts[0]
    assert newest_script["language"] == "python"
    assert newest_script["framework"] == "playwright"
    assert newest_script["syntax_valid"] == "valid"

    # Inspect full script detail (POM page objects and fixtures)
    detail_res = client.get(f"/api/v1/automation/scripts/{newest_script['id']}", headers={"X-Demo-User-Role": "Viewer"})
    assert detail_res.status_code == 200
    script_detail = detail_res.json()
    assert "class Test" in script_detail["test_code"]
    assert len(script_detail["page_objects"]) >= 1

    # 5. Verify that a second ApprovalRequest was queued for Human Code Approval
    pending_code_apps = client.get(f"/api/v1/approvals?project_id=proj-core-payment-gateway&status=pending", headers={"X-Demo-User-Role": "Viewer"}).json()
    code_approval = next((a for a in pending_code_apps if a["workflow_id"] == workflow_id and a["artifact_type"] == "automation_code"), None)
    assert code_approval is not None
    assert code_approval["quality_score"] >= 8.0

    # 6. QA Manager approves the automation code
    code_dec_res = client.post(
        f"/api/v1/approvals/{code_approval['id']}/decision",
        json={"decision": "approved", "reviewer_comment": "Playwright POM code and security audit verified."},
        headers={"X-Demo-User-Role": "QA Manager"}
    )
    assert code_dec_res.status_code == 200
    assert code_dec_res.json()["status"] == "approved"

    # 7. Workflow should now transition to completed following Draft PR and CI dispatch
    wf_updated = client.get(f"/api/v1/workflows/{workflow_id}", headers={"X-Demo-User-Role": "Viewer"}).json()
    assert wf_updated["current_stage"] == "completed"
    assert wf_updated["status"] in ("completed", "failed")
