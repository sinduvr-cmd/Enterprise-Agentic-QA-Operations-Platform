"""
Integration tests for Workflows and Approvals.
"""
def test_trigger_workflow_and_query(client):
    payload = {
        "project_id": "proj-core-payment-gateway",
        "run_name": "Regression Test: Multi-Currency Checkout",
        "requirement_text": "Verify currency conversion rates lock for 30 minutes at checkout.",
        "target_browsers": ["chromium"]
    }
    create_res = client.post("/api/v1/workflows", json=payload, headers={"X-Demo-User-Role": "QA Engineer"})
    assert create_res.status_code == 201
    run = create_res.json()
    assert run["status"] in ("running", "awaiting_approval")
    assert len(run["agent_reasoning_log"]) >= 1

    # Query details
    detail_res = client.get(f"/api/v1/workflows/{run['workflow_id']}", headers={"X-Demo-User-Role": "Viewer"})
    assert detail_res.status_code == 200
    assert detail_res.json()["workflow_id"] == run["workflow_id"]


def test_approvals_list_and_decision(client):
    list_res = client.get("/api/v1/approvals", headers={"X-Demo-User-Role": "Viewer"})
    assert list_res.status_code == 200
    approvals = list_res.json()
    assert len(approvals) >= 1

    pending = next((a for a in approvals if a["status"] == "pending"), None)
    if pending:
        decision_payload = {
            "decision": "approved",
            "reviewer_comment": "Approved during automated test verification"
        }
        dec_res = client.post(
            f"/api/v1/approvals/{pending['id']}/decision",
            json=decision_payload,
            headers={"X-Demo-User-Role": "QA Manager"}
        )
        assert dec_res.status_code == 200
        assert dec_res.json()["status"] == "approved"
