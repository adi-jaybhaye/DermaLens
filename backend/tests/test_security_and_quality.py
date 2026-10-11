import io
import uuid
import numpy as np
from PIL import Image
from starlette.testclient import TestClient

from app.main import app
from app.ml.quality.image_quality import check_image_quality
from app.ml.face.face_processor import detect_face
from app.config.settings import settings
from pathlib import Path

client = TestClient(app)


def _create_test_image_bytes(width=400, height=400, color=(128, 128, 128), fmt="JPEG"):
    """Helper to generate in-memory synthetic image bytes."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def _get_auth_headers():
    email = f"sec_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": pwd, "full_name": "Security Test User"},
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_extension_rejection():
    headers = _get_auth_headers()
    # Create an assessment session
    create_resp = client.post(
        "/api/v1/assessments",
        json={"capture_type": "upload", "views": ["front"]},
        headers=headers,
    )
    assessment_id = create_resp.json()["assessment_id"]

    # 1. Reject invalid extension (.txt)
    txt_file = io.BytesIO(b"malicious script or text")
    resp_txt = client.post(
        f"/api/v1/assessments/{assessment_id}/images?view=front",
        headers=headers,
        files={"file": ("test.txt", txt_file, "text/plain")},
    )
    assert resp_txt.status_code == 400
    assert "Only JPEG, PNG, and WebP" in resp_txt.json()["detail"]

    # 2. Reject invalid MIME type
    resp_bin = client.post(
        f"/api/v1/assessments/{assessment_id}/images?view=front",
        headers=headers,
        files={"file": ("test.jpg", txt_file, "application/octet-stream")},
    )
    assert resp_bin.status_code == 400

    # 3. Reject malformed image bytes
    corrupt_bytes = io.BytesIO(b"not a real image data at all")
    resp_corrupt = client.post(
        f"/api/v1/assessments/{assessment_id}/images?view=front",
        headers=headers,
        files={"file": ("test.jpg", corrupt_bytes, "image/jpeg")},
    )
    assert resp_corrupt.status_code == 400
    assert "corrupted" in resp_corrupt.json()["detail"].lower()

    # 4. Reject tiny dimensions (< 300px)
    tiny_bytes = _create_test_image_bytes(width=150, height=150)
    resp_tiny = client.post(
        f"/api/v1/assessments/{assessment_id}/images?view=front",
        headers=headers,
        files={"file": ("tiny.jpg", io.BytesIO(tiny_bytes), "image/jpeg")},
    )
    assert resp_tiny.status_code == 400
    assert "too low" in resp_tiny.json()["detail"].lower()


def test_image_quality_gate_checks():
    # 1. Dark image check
    dark_bytes = _create_test_image_bytes(width=400, height=400, color=(10, 10, 10))
    res_dark = check_image_quality(dark_bytes)
    assert not res_dark["valid"]
    assert any("dark" in issue.lower() for issue in res_dark["issues"])

    # 2. Overexposed image check
    bright_bytes = _create_test_image_bytes(width=400, height=400, color=(245, 245, 245))
    res_bright = check_image_quality(bright_bytes)
    assert not res_bright["valid"]
    assert any("overexposed" in issue.lower() for issue in res_bright["issues"])

    # 3. Low resolution check
    small_bytes = _create_test_image_bytes(width=200, height=200, color=(128, 128, 128))
    res_small = check_image_quality(small_bytes)
    assert not res_small["valid"]
    assert "too low" in res_small["reason"].lower()

    # 4. Blurry check on flat uniform image
    flat_bytes = _create_test_image_bytes(width=400, height=400, color=(128, 128, 128))
    res_flat = check_image_quality(flat_bytes)
    assert not res_flat["valid"]
    assert any("blurry" in issue.lower() for issue in res_flat["issues"])


def test_face_detector_no_face():
    # An image with no face (uniform flat background)
    non_face_bytes = _create_test_image_bytes(width=400, height=400, color=(120, 140, 160))
    result = detect_face(non_face_bytes)
    assert result is not None
    assert result["success"] is False
    assert result["face_count"] == 0
    assert "no face" in result["reason"].lower()


def test_storage_and_physical_deletion_cleanup():
    headers = _get_auth_headers()
    # Create an assessment
    create_resp = client.post(
        "/api/v1/assessments",
        json={"capture_type": "upload", "views": ["front"]},
        headers=headers,
    )
    assessment_id = create_resp.json()["assessment_id"]

    # 1. Test failed upload cleanup: when processing fails, no orphaned file is left on disk
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    before_files = set(upload_dir.glob("*"))

    img_bytes = _create_test_image_bytes(width=500, height=500, color=(130, 130, 130))
    failed_upload = client.post(
        f"/api/v1/assessments/{assessment_id}/images?view=front",
        headers=headers,
        files={"file": ("front.jpg", io.BytesIO(img_bytes), "image/jpeg")},
    )
    assert failed_upload.status_code == 400  # rejected by quality/face gate
    after_files = set(upload_dir.glob("*"))
    assert after_files == before_files, "Rejected uploads must not leave behind orphaned files on disk"

    # 2. Test successful assessment deletion cleans up any associated image files
    from app.services.image_service import create_image_record
    dummy_file = upload_dir / f"test_cleanup_{uuid.uuid4().hex}.jpg"
    dummy_file.write_bytes(b"dummy image data")
    assert dummy_file.exists()

    create_image_record(
        assessment_id=assessment_id,
        view="front",
        filename="dummy.jpg",
        content_type="image/jpeg",
        file_size=len(b"dummy image data"),
        file_path=str(dummy_file),
    )

    # Delete assessment
    del_resp = client.delete(f"/api/v1/assessments/{assessment_id}", headers=headers)
    assert del_resp.status_code == 200

    # Verify physical file was unlinked
    assert not dummy_file.exists(), "Associated image files must be deleted when the assessment is deleted"
