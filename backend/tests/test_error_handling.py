import io
import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_global_exception_handler_sanitizes_unhandled_errors(monkeypatch):
    """Verify that unhandled exceptions do not leak stack traces or internals."""
    from app.api.routes import assessments
    from tests.test_security_and_quality import _get_auth_headers

    headers = _get_auth_headers()

    def crash_get(*args, **kwargs):
        raise RuntimeError("SecretDatabaseError: connection string exposed on /internal/secret/path.py")

    monkeypatch.setattr(assessments, "get_assessment", crash_get)

    local_client = TestClient(app, raise_server_exceptions=False)
    response = local_client.get("/api/v1/assessments/507f1f77bcf86cd799439011", headers=headers)
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "unexpected internal server error" in data["detail"].lower()

    # Verify absence of leaked Python internals
    assert "secretdatabaseerror" not in data["detail"].lower()
    assert "internal/secret" not in data["detail"].lower()
    assert "traceback" not in data["detail"].lower()


def test_xai_gradcam_error_sanitization():
    """Verify that Grad-CAM failures return safe error messages without Python exceptions."""
    # 1. Empty file rejection
    empty_resp = client.post(
        "/api/v1/xai/gradcam",
        files={"file": ("test.jpg", io.BytesIO(b""), "image/jpeg")},
    )
    assert empty_resp.status_code == 400

    # 2. Unsupported format rejection
    txt_resp = client.post(
        "/api/v1/xai/gradcam",
        files={"file": ("test.txt", io.BytesIO(b"some text"), "text/plain")},
    )
    assert txt_resp.status_code == 400
    assert "Only JPEG, PNG, and WebP" in txt_resp.json()["detail"]

    # 3. Malformed image data triggers safe 500 without leaking stack traces or internal paths
    corrupted_data = io.BytesIO(b"\xff\xd8\xff\xe0malformed corrupted image content")
    err_resp = client.post(
        "/api/v1/xai/gradcam",
        files={"file": ("corrupt.jpg", corrupted_data, "image/jpeg")},
    )
    assert err_resp.status_code in (400, 500)
    detail = err_resp.json().get("detail", "")
    assert "traceback" not in detail.lower()
    assert "file \"" not in detail.lower()
    assert ".py" not in detail.lower()


def test_skin_prediction_error_sanitization():
    """Verify that skin prediction failures return safe error messages."""
    # Malformed image data
    corrupted_data = io.BytesIO(b"corrupted image bytes")
    err_resp = client.post(
        "/api/v1/skin-prediction",
        files={"file": ("bad.jpg", corrupted_data, "image/jpeg")},
    )
    assert err_resp.status_code in (400, 500)
    detail = err_resp.json().get("detail", "")
    assert "traceback" not in detail.lower()
    assert ".py" not in detail.lower()
