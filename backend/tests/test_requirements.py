"""
Integration tests for Requirements ingestion.
"""
def test_requirements_crud(client):
    # 1. List requirements
    res = client.get("/api/v1/requirements?project_id=proj-core-payment-gateway", headers={"X-Demo-User-Role": "QA Engineer"})
    assert res.status_code == 200
    reqs = res.json()
    assert len(reqs) >= 1

    # 2. Post new requirement
    payload = {
        "project_id": "proj-core-payment-gateway",
        "title": "Apple Pay & Google Pay Express Checkout",
        "description": "As a mobile buyer, I want single-tap biometric checkout using Apple Pay so that checkout drop-off reduces.",
        "source": "github_issue",
        "github_issue_url": "https://github.com/enterprise-org/payment-gateway-service/issues/188",
        "github_issue_number": "188",
        "acceptance_criteria": [
            "PaymentRequest API validates browser support",
            "Apple Pay sheet displays authorized billing contact"
        ]
    }
    create_res = client.post("/api/v1/requirements", json=payload, headers={"X-Demo-User-Role": "QA Engineer"})
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["title"] == "Apple Pay & Google Pay Express Checkout"
    assert created["status"] == "draft"
