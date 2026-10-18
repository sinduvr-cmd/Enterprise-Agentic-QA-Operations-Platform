"""
Unit tests for API health and system info endpoints.
"""
def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Enterprise Agentic QA" in data["service"]
    assert data["demo_mode"] is True


def test_system_info_endpoint(client):
    response = client.get("/api/v1/system-info")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "Enterprise Agentic QA Operations Platform"
    assert data["database"] in ("sqlite", "postgresql")
    assert data["llm_provider"] in ("mock", "openai", "gemini")
