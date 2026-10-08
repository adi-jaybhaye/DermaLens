from fastapi import APIRouter, File, HTTPException, UploadFile

from app.ml.face.face_processor import extract_face_regions
from app.ml.skin.skin_analyzer import analyze_skin_regions
from app.ml.model.efficientnet_predictor import predict_skin_concern


router = APIRouter()


@router.post("/skin-prediction")
async def skin_prediction(file: UploadFile = File(...)):
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    try:
        result = predict_skin_concern(contents)
        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Skin prediction failed: {str(exc)}",
        )


@router.post("/skin-analysis")
async def skin_analysis(file: UploadFile = File(...)):
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    try:
        face_result = extract_face_regions(contents)

        if not face_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=face_result,
            )

        skin_result = analyze_skin_regions(
            image_bytes=contents,
            regions=face_result["regions"],
        )

        if not skin_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=skin_result,
            )

        return skin_result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Skin analysis failed: {str(exc)}",
        )