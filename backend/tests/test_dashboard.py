"""
Integration tests for Operations Dashboard endpoints.
"""
def test_dashboard_overview(client):
    response = client.get("/api/v1/dashboard/overview", headers={"X-Demo-User-Role": "Admin"})
    assert response.status_code == 200
    data = response.json()

    # 1. Summary Cards
    summary = data["summary"]
    assert summary["total_qa_runs"] >= 3
    assert summary["running_workflows"] >= 1
    assert summary["active_projects"] >= 3
    assert summary["automation_coverage"] > 0

    # 2. Recent Runs List
    recent_runs = data["recent_runs"]
    assert len(recent_runs) >= 3
    first_run = recent_runs[0]
    assert "workflow_id" in first_run
    assert "status" in first_run
    assert "current_stage" in first_run

    # 3. Agent Activity Timeline
    timeline = data["agent_activity"]
    assert len(timeline) >= 2
    assert any(t["agent_name"] in ("Requirement Analyzer", "Critic Evaluator", "Automation Generator") for t in timeline)

    # 4. Pass/Fail Distribution
    dist = data["pass_fail_distribution"]
    assert "passed" in dist
    assert "failed" in dist
    assert "pass_rate" in dist

    # 5. Requirement Coverage
    coverage = data["requirement_coverage"]
    assert len(coverage) >= 1
    assert "requirement_uid" in coverage[0]
