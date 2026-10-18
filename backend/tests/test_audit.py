"""
Integration tests for Audit Logging.
"""
def test_audit_logs_query(client):
    response = client.get("/api/v1/audit", headers={"X-Demo-User-Role": "Admin"})
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) >= 1

    first_log = logs[0]
    assert "action" in first_log
    assert "resource_type" in first_log
    assert "created_at" in first_log
