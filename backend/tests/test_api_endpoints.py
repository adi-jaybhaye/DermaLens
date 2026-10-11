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


def test_unauthenticated_assessment_access_rejected():
    # 1. Unauthenticated creation is rejected with 401
    create_resp = client.post(
        "/api/v1/assessments",
        json={"capture_type": "upload", "views": ["front"]},
    )
    assert create_resp.status_code == 401

    # 2. Unauthenticated history is rejected with 401
    history_resp = client.get("/api/v1/assessments/history")
    assert history_resp.status_code == 401

    # 3. Unauthenticated access to specific assessment is rejected with 401
    get_resp = client.get("/api/v1/assessments/507f1f77bcf86cd799439011")
    assert get_resp.status_code == 401

    # 4. Unauthenticated deletion is rejected with 401
    del_resp = client.delete("/api/v1/assessments/507f1f77bcf86cd799439011")
    assert del_resp.status_code == 401


def test_assessment_lifecycle():
    # Setup test user and authenticate
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pwd, "full_name": "Assessment User"},
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create assessment
    create_resp = client.post(
        "/api/v1/assessments",
        json={
            "capture_type": "hybrid",
            "capture_modes": {"front": "camera", "left": "upload", "right": "upload"},
            "views": ["front", "left", "right"],
        },
        headers=headers,
    )
    assert create_resp.status_code == 200
    data = create_resp.json()
    assessment_id = data["assessment_id"]
    assert data["status"] == "created"

    # 2. Get assessment
    get_resp = client.get(f"/api/v1/assessments/{assessment_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == assessment_id
    assert get_resp.json()["capture_type"] == "hybrid"
    assert get_resp.json()["capture_modes"] == {"front": "camera", "left": "upload", "right": "upload"}

    # 3. Status endpoint
    status_resp = client.get(f"/api/v1/assessments/{assessment_id}/status", headers=headers)
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["assessment_id"] == assessment_id

    # 4. History endpoint
    history_resp = client.get("/api/v1/assessments/history", headers=headers)
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert isinstance(history, list)
    assert any(item["id"] == assessment_id for item in history)

    # 5. Delete assessment
    del_resp = client.delete(f"/api/v1/assessments/{assessment_id}", headers=headers)
    assert del_resp.status_code == 200

    # 6. Verify deleted
    get_again = client.get(f"/api/v1/assessments/{assessment_id}", headers=headers)
    assert get_again.status_code == 404


def test_cross_user_authorization_isolation():
    # Create User A
    user_a_email = f"usera_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg_a = client.post(
        "/api/v1/auth/register",
        json={"email": user_a_email, "password": pwd, "full_name": "User A"},
    )
    token_a = reg_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Create User B
    user_b_email = f"userb_{uuid.uuid4().hex[:8]}@example.com"
    reg_b = client.post(
        "/api/v1/auth/register",
        json={"email": user_b_email, "password": pwd, "full_name": "User B"},
    )
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates an assessment
    create_resp = client.post(
        "/api/v1/assessments",
        json={"capture_type": "upload", "views": ["front"]},
        headers=headers_a,
    )
    assert create_resp.status_code == 200
    assessment_id = create_resp.json()["assessment_id"]

    # User B attempts to access User A's assessment -> 403 Forbidden
    get_b = client.get(f"/api/v1/assessments/{assessment_id}", headers=headers_b)
    assert get_b.status_code == 403

    # User B attempts to access User A's status -> 403 Forbidden
    status_b = client.get(f"/api/v1/assessments/{assessment_id}/status", headers=headers_b)
    assert status_b.status_code == 403

    # User B attempts to trigger analysis on User A's assessment -> 403 Forbidden
    analyze_b = client.post(f"/api/v1/assessments/{assessment_id}/analyze", headers=headers_b)
    assert analyze_b.status_code == 403

    # User B attempts to get User A's results -> 403 Forbidden
    results_b = client.get(f"/api/v1/assessments/{assessment_id}/results", headers=headers_b)
    assert results_b.status_code == 403

    # User B attempts to delete User A's assessment -> 403 Forbidden
    del_b = client.delete(f"/api/v1/assessments/{assessment_id}", headers=headers_b)
    assert del_b.status_code == 403

    # User B's history must NOT contain User A's assessment
    hist_b = client.get("/api/v1/assessments/history", headers=headers_b)
    assert hist_b.status_code == 200
    assert not any(item["id"] == assessment_id for item in hist_b.json())

    # User A successfully accesses and deletes own assessment
    get_a = client.get(f"/api/v1/assessments/{assessment_id}", headers=headers_a)
    assert get_a.status_code == 200
    del_a = client.delete(f"/api/v1/assessments/{assessment_id}", headers=headers_a)
    assert del_a.status_code == 200


def test_consent_metadata_and_account_deletion_wipe():
    # 1. Register with consent
    email = f"privacy_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": pwd,
            "full_name": "Privacy User",
            "consent_version": "1.0",
        },
    )
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data["user"]["consent_version"] == "1.0"
    assert "consented_at" in reg_data["user"]
    token = reg_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Check profile reflects consent metadata
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["consent_version"] == "1.0"

    # 3. Create assessment with consent metadata
    create_resp = client.post(
        "/api/v1/assessments",
        json={
            "capture_type": "upload",
            "views": ["front"],
            "consent_version": "1.0",
        },
        headers=headers,
    )
    assert create_resp.status_code == 200
    assessment_id = create_resp.json()["assessment_id"]

    # Verify assessment stores consent
    get_resp = client.get(f"/api/v1/assessments/{assessment_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["consent_version"] == "1.0"

    # 4. Create an associated dummy file in uploads to verify unlinking upon account deletion
    from pathlib import Path
    from app.config.settings import settings
    from app.services.image_service import create_image_record

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dummy_file = upload_dir / f"privacy_test_{uuid.uuid4().hex}.jpg"
    dummy_file.write_bytes(b"facial image biometric payload")
    assert dummy_file.exists()

    create_image_record(
        assessment_id=assessment_id,
        view="front",
        filename="face.jpg",
        content_type="image/jpeg",
        file_size=len(b"facial image biometric payload"),
        file_path=str(dummy_file),
    )

    # 5. Execute account deletion (data wipe)
    del_acc_resp = client.delete("/api/v1/auth/me", headers=headers)
    assert del_acc_resp.status_code == 200

    # 6. Verify account is gone: auth token is no longer valid
    me_after = client.get("/api/v1/auth/me", headers=headers)
    assert me_after.status_code == 401

    # 7. Verify assessment is completely removed from DB
    from app.config.database import database
    from bson import ObjectId
    assert database.assessment_sessions.find_one({"_id": ObjectId(assessment_id)}) is None
    assert database.assessment_images.find_one({"assessment_id": assessment_id}) is None

    # 8. Verify physical file on disk was unlinked
    assert not dummy_file.exists(), "Account deletion must wipe physical image artifacts from disk"


