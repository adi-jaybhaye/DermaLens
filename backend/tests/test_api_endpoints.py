import io
import uuid
import numpy as np
from PIL import Image
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert "service" in data


def test_knowledge_endpoints():
    # 1. List all concerns
    resp = client.get("/api/v1/knowledge")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 8
    assert len(data["concerns"]) == 8

    # 2. Get specific concern
    resp = client.get("/api/v1/knowledge/Redness")
    assert resp.status_code == 200
    redness = resp.json()
    assert redness["concept"] == "Redness"
    assert "why_it_can_occur" in redness
    assert "visual_characteristics" in redness
    assert "evidence_references" in redness

    # 3. Not found concern
    resp = client.get("/api/v1/knowledge/non_existent_concern")
    assert resp.status_code == 404

    # 4. Safety endpoint
    resp = client.get("/api/v1/safety")
    assert resp.status_code == 200
    safety = resp.json()
    assert safety["disclaimer"] is not None
    assert safety["model_info"]["name"] == "EfficientNet-B0"
    assert safety["model_info"]["validation_accuracy"] == 0.9289


def test_sources_endpoints():
    # 1. List all sources
    resp = client.get("/api/v1/sources")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    source_id = data["sources"][0]["id"]

    # 2. Get source by ID
    resp = client.get(f"/api/v1/sources/{source_id}")
    assert resp.status_code == 200
    source = resp.json()
    assert source["id"] == source_id
    assert "title" in source

    # 3. Not found source
    resp = client.get("/api/v1/sources/non_existent_id")
    assert resp.status_code == 404


def test_auth_flow():
    test_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "SecurePassword123!"

    # 1. Register
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "full_name": "Test User",
        },
    )
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    token = reg_data["access_token"]
    assert reg_data["user"]["email"] == test_email

    # 2. Duplicate register fails
    dup_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_email,
            "password": test_password,
        },
    )
    assert dup_resp.status_code == 400

    # 3. Login wrong password fails
    wrong_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_email,
            "password": "WrongPassword",
        },
    )
    assert wrong_login.status_code == 401

    # 4. Login correct password succeeds
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_email,
            "password": test_password,
        },
    )
    assert login_resp.status_code == 200
    login_token = login_resp.json()["access_token"]

    # 5. Get current user profile with token
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login_token}"},
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == test_email

    # 6. Get profile without token fails
    unauth_resp = client.get("/api/v1/auth/me")
    assert unauth_resp.status_code == 401


def test_assessment_lifecycle():
    # 1. Create assessment
    create_resp = client.post(
        "/api/v1/assessments",
        json={
            "capture_type": "upload",
            "views": ["front", "left", "right"],
        },
    )
    assert create_resp.status_code == 200
    data = create_resp.json()
    assessment_id = data["assessment_id"]
    assert data["status"] == "created"

    # 2. Get assessment
    get_resp = client.get(f"/api/v1/assessments/{assessment_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == assessment_id

    # 3. Status endpoint
    status_resp = client.get(f"/api/v1/assessments/{assessment_id}/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["assessment_id"] == assessment_id

    # 4. History endpoint
    history_resp = client.get("/api/v1/assessments/history")
    assert history_resp.status_code == 200
    assert isinstance(history_resp.json(), list)

    # 5. Delete assessment
    del_resp = client.delete(f"/api/v1/assessments/{assessment_id}")
    assert del_resp.status_code == 200

    # 6. Verify deleted
    get_again = client.get(f"/api/v1/assessments/{assessment_id}")
    assert get_again.status_code == 404
