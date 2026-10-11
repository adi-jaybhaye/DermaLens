import logging
from fastapi import APIRouter, File, HTTPException, UploadFile, Request, status

from app.ml.face.face_processor import extract_face_regions
from app.ml.skin.skin_analyzer import analyze_skin_regions
from app.ml.model.efficientnet_predictor import predict_skin_concern
from app.utils.rate_limiter import upload_limiter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/skin-prediction")
async def skin_prediction(request: Request, file: UploadFile = File(...)):
    upload_limiter.check(request)
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    try:
        result = predict_skin_concern(contents)
        return result

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Skin prediction failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Skin concern prediction could not be completed. Please try again with a valid image.",
        )


@router.post("/skin-analysis")
async def skin_analysis(request: Request, file: UploadFile = File(...)):
    upload_limiter.check(request)
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    try:
        face_result = extract_face_regions(contents)

        if not face_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=face_result,
            )

        skin_result = analyze_skin_regions(
            image_bytes=contents,
            regions=face_result["regions"],
        )

        if not skin_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=skin_result,
            )

        return skin_result

    except HTTPException:
        raise

    except Exception as exc:
        logger.error(f"Skin analysis failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Skin analysis could not be completed. Please try again with a valid image.",
        )