"""
Tests des Endpoints REST FastAPI
"""
from fastapi.testclient import TestClient

from src.infrastructure.fastapi_app import app

client = TestClient(app)


def test_analyze_contract_endpoint_success():
    payload = {
        "filename": "accord_cadre.pdf",
        "raw_content": "Accord B2B sans clauses de pénalités. Responsabilité standard.",
        "tier": "POOL"
    }
    headers = {
        "X-Tenant-ID": "tenant-pme-bordeaux"
    }

    response = client.post("/api/v1/contracts/analyze", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == "tenant-pme-bordeaux"
    assert data["requires_human_review"] is False
    assert data["overall_risk_score"] < 0.15


def test_analyze_contract_endpoint_missing_tenant_header():
    payload = {
        "filename": "accord_cadre.pdf",
        "raw_content": "Accord B2B sans clauses de pénalités.",
        "tier": "POOL"
    }
    # Pas de header X-Tenant-ID
    response = client.post("/api/v1/contracts/analyze", json=payload)
    assert response.status_code == 400
    assert "X-Tenant-ID" in response.json()["detail"]
