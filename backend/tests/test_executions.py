"""
Integration tests for CI Executions and AI Failure Analysis.
"""
def test_executions_and_failure_analysis(client):
    res = client.get("/api/v1/executions", headers={"X-Demo-User-Role": "Viewer"})
    assert res.status_code == 200
    executions = res.json()
    assert len(executions) >= 2

    # Verify passed execution
    passed_exec = next((e for e in executions if e["status"] == "passed"), None)
    assert passed_exec is not None
    assert passed_exec["passed_tests"] > 0
    assert passed_exec["failed_tests"] == 0

    # Verify failed execution with failure analysis
    failed_exec = next((e for e in executions if e["status"] == "failed"), None)
    assert failed_exec is not None
    detail_res = client.get(f"/api/v1/executions/{failed_exec['id']}", headers={"X-Demo-User-Role": "Viewer"})
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["test_results"]) >= 1

    failed_result = detail["test_results"][0]
    assert failed_result["status"] == "failed"
    assert failed_result["failure_analysis"] is not None
    assert failed_result["failure_analysis"]["root_cause_category"] == "locator_issue"
    assert failed_result["failure_analysis"]["confidence_score"] >= 0.90
