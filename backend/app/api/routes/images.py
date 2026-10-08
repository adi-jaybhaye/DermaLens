
import io
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image

from app.schemas.image import ImageResponse
from app.services.image_service import (
    assessment_exists,
    create_image_record,
)
from app.services.assessment_service import process_assessment_image


router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post(
    "/assessments/{assessment_id}/images",
    response_model=ImageResponse,
)
async def upload_assessment_image(
    assessment_id: str,
    view: str,
    file: UploadFile = File(...),
):
    # Check assessment
    if not assessment_exists(assessment_id):
        raise HTTPException(
            status_code=404,
            detail="Assessment not found",
        )

    # Validate view
    view = view.lower()

    if view not in {"front", "left", "right"}:
        raise HTTPException(
            status_code=400,
            detail="View must be one of: front, left, right",
        )

    # Validate file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, and WEBP images are supported",
        )

    contents = await file.read()

    # Validate empty file
    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 10 MB",
        )

    # Validate actual image
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid image",
        )

    # Generate filename and save image BEFORE ML pipeline
    # so the file_path can be stored in the assessment document.
    extension_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    extension = extension_map[file.content_type]
    generated_filename = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / generated_filename

    file_path.write_bytes(contents)

    # Run ML preprocessing pipeline
    processing_result = process_assessment_image(
        assessment_id=assessment_id,
        image_bytes=contents,
        view=view,
        file_path=str(file_path),
    )

    if not processing_result["success"]:
        # Clean up saved file on failure
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail=processing_result,
        )

    # Create database image record
    image_id = create_image_record(
        assessment_id=assessment_id,
        view=view,
        filename=file.filename or generated_filename,
        content_type=file.content_type,
        file_size=len(contents),
        file_path=str(file_path),
    )

    return ImageResponse(
        id=image_id,
        assessment_id=assessment_id,
        view=view,
        filename=file.filename or generated_filename,
        content_type=file.content_type,
        file_size=len(contents),
        file_path=str(file_path),
        created_at=datetime.now(timezone.utc),
    )
