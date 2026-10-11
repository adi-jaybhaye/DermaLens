import logging
from fastapi import APIRouter, File, HTTPException, UploadFile, Request, status

from app.ml.face.face_processor import extract_face_regions
from app.utils.rate_limiter import upload_limiter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/face-analysis")
async def face_analysis(request: Request, file: UploadFile = File(...)):
    upload_limiter.check(request)
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    try:
        result = extract_face_regions(contents)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Face region extraction failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face region extraction failed. Please ensure a clear facial photograph is provided.",
        )

    return result