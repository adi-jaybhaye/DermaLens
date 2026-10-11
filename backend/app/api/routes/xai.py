import logging
from fastapi import APIRouter, File, HTTPException, UploadFile, Request, status

from app.ml.xai.gradcam import generate_gradcam
from app.utils.rate_limiter import upload_limiter

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024


@router.post("/xai/gradcam")
async def gradcam_analysis(request: Request, file: UploadFile = File(...)):
    """Generate a Grad-CAM visual focus heatmap for a standalone image.

    Returns the predicted concern, confidence, class probabilities,
    and base64-encoded visual heatmap and overlay representations.
    """
    upload_limiter.check(request)

    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WebP images are supported",
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size exceeds maximum limit of 10 MB",
        )

    try:
        result = generate_gradcam(contents)
        return result

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Grad-CAM generation failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Visual focus heatmap generation failed. Please try again with a valid, clear image.",
        )

