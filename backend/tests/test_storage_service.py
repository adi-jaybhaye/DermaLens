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
