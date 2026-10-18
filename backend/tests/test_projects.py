"""
Integration tests for Project Management endpoints: List, Create, View, Update, Archive.
"""
def test_list_projects(client):
    response = client.get("/api/v1/projects", headers={"X-Demo-User-Role": "Admin"})
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) >= 3

    # Verify Core Payment Gateway project
    payment_proj = next((p for p in projects if p["id"] == "proj-core-payment-gateway"), None)
    assert payment_proj is not None
    assert payment_proj["name"] == "Core Payment Gateway"
    assert payment_proj["default_branch"] == "main"
    assert payment_proj["framework_config"]["framework"] == "playwright-python"


import uuid

def test_create_and_archive_project(client):
    # 1. Create a new project with unique ID
    unique_id = f"proj-auth-identity-{uuid.uuid4().hex[:6]}"
    payload = {
        "id": unique_id,
        "name": "Auth Identity Service",
        "description": "OAuth2 and OIDC token issuer with MFA.",
        "source_repo": "https://github.com/enterprise-org/auth-identity-service",
        "automation_repo": "https://github.com/enterprise-org/qa-auth-playwright",
        "default_branch": "main",
        "framework_config": {
            "framework": "playwright-python",
            "test_runner": "pytest",
            "pattern": "Page Object Model",
            "base_url": "https://auth.staging.example.com",
            "browsers": ["chromium", "firefox"],
            "headless": True
        }
    }
    create_res = client.post("/api/v1/projects", json=payload, headers={"X-Demo-User-Role": "QA Manager"})
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["id"] == unique_id
    assert created["is_archived"] is False

    # 2. Verify project-level authorization: non-member QA Engineer cannot view (403)
    unauthorized_res = client.get(f"/api/v1/projects/{unique_id}", headers={"X-Demo-User-Role": "QA Engineer"})
    assert unauthorized_res.status_code == 403

    # Authorized member (QA Manager creator) or Admin can view (200)
    detail_res = client.get(f"/api/v1/projects/{unique_id}", headers={"X-Demo-User-Role": "QA Manager"})
    assert detail_res.status_code == 200
    assert detail_res.json()["name"] == "Auth Identity Service"

    # 3. Archive project
    archive_res = client.patch(f"/api/v1/projects/{unique_id}/archive", headers={"X-Demo-User-Role": "QA Manager"})
    assert archive_res.status_code == 200
    assert archive_res.json()["is_archived"] is True

    # 4. Unarchive project
    unarchive_res = client.patch(f"/api/v1/projects/{unique_id}/archive", headers={"X-Demo-User-Role": "QA Manager"})
    assert unarchive_res.status_code == 200
    assert unarchive_res.json()["is_archived"] is False

