import uuid
import pytest
from starlette.testclient import TestClient
from app.main import app
from app.schemas.assessment import AssessmentCreate

client = TestClient(app)


def test_persistent_assessment_numbering():
    # 0. Register and login a fresh user
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pwd, "full_name": "Naming Tester"}
    )
    assert reg_resp.status_code == 200
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create first assessment
    data1 = AssessmentCreate(views=["front"], capture_type="upload")
    res1 = client.post("/api/v1/assessments", json=data1.model_dump(), headers=headers)
    assert res1.status_code == 200
    id1 = res1.json()["assessment_id"]

    # 2. Create second assessment
    data2 = AssessmentCreate(views=["front", "left", "right"], capture_type="camera")
    res2 = client.post("/api/v1/assessments", json=data2.model_dump(), headers=headers)
    assert res2.status_code == 200
    id2 = res2.json()["assessment_id"]

    # 3. Retrieve assessment 1 and 2
    session1 = client.get(f"/api/v1/assessments/{id1}", headers=headers).json()
    session2 = client.get(f"/api/v1/assessments/{id2}", headers=headers).json()

    assert session1["assessment_number"] == 1
    assert session2["assessment_number"] == 2
    assert session1["name"] == "Assessment 1"
    assert session2["name"] == "Assessment 2"

    # 4. History list contains persistent assessment_number and name
    history = client.get("/api/v1/assessments/history", headers=headers).json()
    assert len(history) == 2
    found1 = next(item for item in history if item["id"] == id1)
    found2 = next(item for item in history if item["id"] == id2)
    assert found1["name"] == "Assessment 1"
    assert found2["name"] == "Assessment 2"
    assert found1["assessment_number"] == 1
    assert found2["assessment_number"] == 2

    # 5. Rename assessment 1
    rename_res = client.patch(
        f"/api/v1/assessments/{id1}/rename",
        json={"name": "Autumn Skin Check"},
        headers=headers,
    )
    assert rename_res.status_code == 200
    assert rename_res.json()["name"] == "Autumn Skin Check"

    # Verify persisted in get and history
    session1_updated = client.get(f"/api/v1/assessments/{id1}", headers=headers).json()
    assert session1_updated["name"] == "Autumn Skin Check"
    assert session1_updated["assessment_number"] == 1  # Number stays stable!

    # Clean up
    client.delete(f"/api/v1/assessments/{id1}", headers=headers)
    client.delete(f"/api/v1/assessments/{id2}", headers=headers)


def test_atomic_numbering_on_deletion_and_abandonment():
    """Verify that deleting an assessment does not cause sequential number reuse,
    and test abandonment lifecycle transition.
    """
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pwd, "full_name": "Atomic Sequence Tester"}
    )
    assert reg_resp.status_code == 200
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Assessment 1
    r1 = client.post("/api/v1/assessments", json={"views": ["front"], "capture_type": "upload"}, headers=headers)
    id1 = r1.json()["assessment_id"]
    sess1 = client.get(f"/api/v1/assessments/{id1}", headers=headers).json()
    assert sess1["assessment_number"] == 1
    assert sess1["name"] == "Assessment 1"

    # 2. Create Assessment 2
    r2 = client.post("/api/v1/assessments", json={"views": ["front"], "capture_type": "upload"}, headers=headers)
    id2 = r2.json()["assessment_id"]
    sess2 = client.get(f"/api/v1/assessments/{id2}", headers=headers).json()
    assert sess2["assessment_number"] == 2
    assert sess2["name"] == "Assessment 2"

    # 3. Delete Assessment 2
    del_res = client.delete(f"/api/v1/assessments/{id2}", headers=headers)
    assert del_res.status_code == 200

    # 4. Create next assessment — MUST get assessment_number 3, NOT reuse 2!
    r3 = client.post("/api/v1/assessments", json={"views": ["front"], "capture_type": "upload"}, headers=headers)
    id3 = r3.json()["assessment_id"]
    sess3 = client.get(f"/api/v1/assessments/{id3}", headers=headers).json()
    assert sess3["assessment_number"] == 3
    assert sess3["name"] == "Assessment 3"

    # 5. Abandon Assessment 3
    abandon_res = client.post(f"/api/v1/assessments/{id3}/abandon", headers=headers)
    assert abandon_res.status_code == 200
    assert abandon_res.json()["status"] == "abandoned"

    sess3_abandoned = client.get(f"/api/v1/assessments/{id3}", headers=headers).json()
    assert sess3_abandoned["status"] == "abandoned"

    # Clean up
    client.delete(f"/api/v1/assessments/{id1}", headers=headers)
    client.delete(f"/api/v1/assessments/{id3}", headers=headers)
