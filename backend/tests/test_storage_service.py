import pytest
from app.services.storage_service import storage_service
from app.config.settings import settings


def test_storage_service_local_save_read_delete():
    """Verify local private filesystem save, read, and delete operations."""
    test_content = b"sample_skin_assessment_image_bytes_12345"
    save_result = storage_service.save_file(
        file_bytes=test_content,
        filename="test_skin.jpg",
        content_type="image/jpeg",
    )
    assert "storage_key" in save_result
    assert "file_path" in save_result
    assert save_result["storage_type"] == "local"

    # Read back
    read_bytes = storage_service.read_file(save_result["file_path"])
    assert read_bytes == test_content

    # Delete
    deleted = storage_service.delete_file(save_result["file_path"])
    assert deleted is True

    # Confirm non-existent raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        storage_service.read_file(save_result["file_path"])


def test_storage_service_deletion_audit_report():
    """Verify delete_assessment_files returns structured report and handles missing files gracefully."""
    # 1. Save two dummy files
    f1 = storage_service.save_file(b"dummy1", filename="view1.jpg")
    f2 = storage_service.save_file(b"dummy2", filename="view2.jpg")

    mock_assessment = {
        "images": {
            "front": {"file_path": f1["file_path"]},
            "left": {"file_path": f2["file_path"]},
        }
    }
    mock_records = [
        {"file_path": f1["file_path"]},
        {"file_path": f2["file_path"]},
        {"file_path": "uploads/non_existent_path.jpg"},  # one non-existent
    ]

    report = storage_service.delete_assessment_files(mock_assessment, mock_records)
    assert "total_expected" in report
    assert "deleted_count" in report
    assert "failed_paths" in report
    assert "success" in report
    assert report["deleted_count"] == 2
    assert "uploads/non_existent_path.jpg" in report["failed_paths"]
    assert report["success"] is False  # Because one failed


def test_storage_service_production_failfast(monkeypatch):
    """Verify that in production mode, missing Azure connection string fails fast with RuntimeError."""
    from app.services.storage_service import StorageService

    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "azure_storage_connection_string", "")

    with pytest.raises(RuntimeError) as exc_info:
        StorageService()
    assert "AZURE_STORAGE_CONNECTION_STRING" in str(exc_info.value)
    assert "strictly prohibited" in str(exc_info.value)



def test_delete_assessment_storage_failure_retains_db_record(monkeypatch):
    """Verify that if physical image storage deletion fails, database records are NOT deleted
    and status transitions to 'cleanup_pending'.
    """
    from app.services.assessment_service import delete_assessment, create_assessment
    from app.schemas.assessment import AssessmentCreate
    from app.config.database import database
    from bson import ObjectId

    # 1. Create a real assessment
    data = AssessmentCreate(views=["front"], capture_type="upload")
    assessment_id = create_assessment(data, user_id="test_user_storage_fail")
    assert assessment_id is not None

    # 2. Simulate storage deletion failure
    def mock_delete_files(*args, **kwargs):
        return {
            "total_expected": 1,
            "deleted_count": 0,
            "failed_paths": ["azure://assessment-images/front_view.jpg"],
            "success": False,
        }

    monkeypatch.setattr(storage_service, "delete_assessment_files", mock_delete_files)

    # 3. Attempt deletion — MUST return False
    result = delete_assessment(assessment_id, user_id="test_user_storage_fail")
    assert result is False

    # 4. Verify database record was NOT deleted!
    record = database.assessment_sessions.find_one({"_id": ObjectId(assessment_id)})
    assert record is not None, "Database record must be retained when storage deletion fails!"
    assert record["status"] == "cleanup_pending"
    assert "azure://assessment-images/front_view.jpg" in record["failed_storage_paths"]

    # 5. Clean up test document safely
    database.assessment_sessions.delete_one({"_id": ObjectId(assessment_id)})


def test_abandon_assessment_storage_failure_retains_metadata(monkeypatch):
    """Verify that if storage deletion fails during abandonment:
    - abandon_assessment() returns False
    - Assessment document is retained and set to 'cleanup_pending'
    - Image records in assessment_images collection are NOT wiped
    """
    from app.services.assessment_service import create_assessment, abandon_assessment
    from app.services.image_service import create_image_record
    from app.schemas.assessment import AssessmentCreate
    from app.config.database import database
    from app.services.storage_service import storage_service
    from bson import ObjectId

    # 1. Create an assessment
    data = AssessmentCreate(views=["front"], capture_type="upload")
    assessment_id = create_assessment(data, user_id="test_abandon_user")
    assert assessment_id is not None

    # 2. Add an image record
    create_image_record(
        assessment_id=assessment_id,
        view="front",
        filename="test_abandon.jpg",
        content_type="image/jpeg",
        file_size=1024,
        file_path="uploads/test_abandon.jpg",
    )

    # 3. Mock storage failure
    def mock_delete_files(*args, **kwargs):
        return {
            "total_expected": 1,
            "deleted_count": 0,
            "failed_paths": ["uploads/test_abandon.jpg"],
            "success": False,
        }

    monkeypatch.setattr(storage_service, "delete_assessment_files", mock_delete_files)

    # 4. Attempt abandon — MUST return False
    res = abandon_assessment(assessment_id, user_id="test_abandon_user")
    assert res is False

    # 5. Verify database records are retained
    session = database.assessment_sessions.find_one({"_id": ObjectId(assessment_id)})
    assert session is not None
    assert session["status"] == "cleanup_pending"
    assert "uploads/test_abandon.jpg" in session["failed_storage_paths"]

    # Image metadata must NOT be deleted
    image_record = database.assessment_images.find_one({"assessment_id": ObjectId(assessment_id)})
    assert image_record is not None, "Image records must not be deleted when storage cleanup fails during abandonment!"

    # Clean up
    database.assessment_images.delete_many({"assessment_id": ObjectId(assessment_id)})
    database.assessment_sessions.delete_one({"_id": ObjectId(assessment_id)})


def test_account_deletion_storage_failure_blocks_user_deletion(monkeypatch):
    """Verify that if any assessment storage cleanup fails during account deletion:
    - delete_user_account() returns success=False
    - User document is NOT deleted
    - Assessment document is NOT deleted and marked 'cleanup_pending'
    - No false 'permanently deleted' response is returned
    """
    from app.services.auth_service import register_user, delete_user_account
    from app.services.assessment_service import create_assessment
    from app.schemas.user import UserCreate
    from app.schemas.assessment import AssessmentCreate
    from app.config.database import database
    from app.services.storage_service import storage_service
    from bson import ObjectId
    import uuid

    email = f"storage_fail_{uuid.uuid4().hex[:8]}@example.com"
    reg = register_user(UserCreate(email=email, password="ValidPassword123!", full_name="Fail User"))
    assert reg["success"] is True
    user_id = reg["user"]["id"]

    # Create assessment for this user
    data = AssessmentCreate(views=["front"], capture_type="upload")
    assessment_id = create_assessment(data, user_id=user_id)
    assert assessment_id is not None

    # Mock storage failure during deletion
    def mock_delete_files(*args, **kwargs):
        return {
            "total_expected": 1,
            "deleted_count": 0,
            "failed_paths": ["azure://assessment-images/orphaned_photo.jpg"],
            "success": False,
        }

    monkeypatch.setattr(storage_service, "delete_assessment_files", mock_delete_files)

    # Attempt account deletion — MUST fail safely
    result = delete_user_account(user_id)
    assert result["success"] is False
    assert "Biometric data cleanup failed" in result["reason"]
    assert assessment_id in result["failed_assessments"]

    # Verify user STILL exists in database
    user_doc = database.users.find_one({"_id": ObjectId(user_id)})
    assert user_doc is not None, "User account must NOT be deleted if biometric storage cleanup fails!"

    # Verify assessment STILL exists in database and is marked cleanup_pending
    assessment_doc = database.assessment_sessions.find_one({"_id": ObjectId(assessment_id)})
    assert assessment_doc is not None, "Assessment record must NOT be deleted if storage cleanup fails!"
    assert assessment_doc["status"] == "cleanup_pending"
    assert "azure://assessment-images/orphaned_photo.jpg" in assessment_doc["failed_storage_paths"]

    # Clean up test artifacts safely
    monkeypatch.undo()
    database.assessment_sessions.delete_one({"_id": ObjectId(assessment_id)})
    database.users.delete_one({"_id": ObjectId(user_id)})
