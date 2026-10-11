
import io
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from bson import ObjectId

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends, Request, status
from PIL import Image, ImageOps

from app.config.database import database
from app.schemas.image import ImageResponse
from app.services.image_service import create_image_record
from app.services.assessment_service import process_assessment_image
from app.api.deps import get_current_user, verify_assessment_ownership
from app.utils.rate_limiter import upload_limiter


router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 10 * 1024 * 1024
MIN_DIMENSION = 300
MAX_DIMENSION = 4096
Image.MAX_IMAGE_PIXELS = 25_000_000  # Decompression bomb guard


@router.post(
    "/assessments/{assessment_id}/images",
    response_model=ImageResponse,
)
async def upload_assessment_image(
    assessment_id: str,
    view: str,
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Secure image upload endpoint with ownership validation and rate limiting."""
    upload_limiter.check(request)

    if not ObjectId.is_valid(assessment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assessment ID",
        )

    # Check assessment existence and verify ownership
    assessment = database.assessment_sessions.find_one(
        {"_id": ObjectId(assessment_id)}
    )
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    verify_assessment_ownership(assessment, current_user)

    # Validate view
    view = view.lower().strip()
    if view not in {"front", "left", "right"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="View must be one of: front, left, right",
        )

    # Validate declared MIME type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WebP images are supported",
        )

    contents = await file.read()

    # Validate empty file
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size must not exceed 10 MB",
        )

    # Validate actual image format and dimensions using PIL
    try:
        image_stream = io.BytesIO(contents)
        with Image.open(image_stream) as pil_image:
            pil_image.verify()
            format_name = (pil_image.format or "").upper()
            if format_name not in {"JPEG", "PNG", "WEBP"}:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File header does not match a supported image format (JPEG, PNG, WebP)",
                )

        # Reopen to read image dimensions safely
        with Image.open(io.BytesIO(contents)) as pil_image:
            width, height = pil_image.size
            if width < MIN_DIMENSION or height < MIN_DIMENSION:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image resolution too low ({width}x{height}). Minimum required is {MIN_DIMENSION}x{MIN_DIMENSION}.",
                )
            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image dimensions exceed maximum supported limit ({MAX_DIMENSION}x{MAX_DIMENSION}).",
                )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is corrupted or not a valid image",
        )

    # Generate filename and save image
    extension_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    extension = extension_map.get(file.content_type, ".jpg")
    storage_key = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / storage_key

    file_path.write_bytes(contents)

    # Run ML preprocessing pipeline
    processing_result = process_assessment_image(
        assessment_id=assessment_id,
        image_bytes=contents,
        view=view,
        file_path=str(file_path),
    )

    if not processing_result["success"]:
        # Clean up saved file on failure to avoid orphaned files
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=processing_result,
        )

    # Create database image record
    image_id = create_image_record(
        assessment_id=assessment_id,
        view=view,
        filename=file.filename or storage_key,
        content_type=file.content_type,
        file_size=len(contents),
        file_path=str(file_path),
    )

    return ImageResponse(
        id=image_id,
        assessment_id=assessment_id,
        view=view,
        filename=file.filename or storage_key,
        content_type=file.content_type,
        file_size=len(contents),
        storage_key=storage_key,
        created_at=datetime.now(timezone.utc),
    )
