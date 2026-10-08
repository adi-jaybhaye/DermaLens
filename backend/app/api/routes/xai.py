from fastapi import APIRouter, File, HTTPException, UploadFile

from app.ml.xai.gradcam import generate_gradcam


router = APIRouter()


@router.post("/xai/gradcam")
async def gradcam_analysis(file: UploadFile = File(...)):
    """Generate a Grad-CAM heatmap for a standalone image.

    Returns the predicted concern, confidence, all class probabilities,
    and base64-encoded heatmap / overlay images.
    """
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    try:
        result = generate_gradcam(contents)
        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Grad-CAM generation failed: {str(exc)}",
        )
