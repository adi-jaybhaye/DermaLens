from datetime import datetime, timezone

from bson import ObjectId

from app.config.database import database


def assessment_exists(assessment_id: str) -> bool:
    try:
        object_id = ObjectId(assessment_id)
    except Exception:
        return False

    return database.assessment_sessions.find_one(
        {"_id": object_id},
        {"_id": 1},
    ) is not None


def create_image_record(
    assessment_id: str,
    view: str,
    filename: str,
    content_type: str,
    file_size: int,
    file_path: str,
) -> str:

    now = datetime.now(timezone.utc)

    document = {
        "assessment_id": ObjectId(assessment_id),
        "view": view,
        "filename": filename,
        "content_type": content_type,
        "file_size": file_size,
        "file_path": file_path,
        "created_at": now,
    }

    result = database.assessment_images.insert_one(document)

    return str(result.inserted_id)