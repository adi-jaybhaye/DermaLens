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
