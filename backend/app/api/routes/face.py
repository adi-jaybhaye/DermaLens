from fastapi import APIRouter, File, HTTPException, UploadFile

from app.ml.face.face_processor import extract_face_regions


router = APIRouter()


@router.post("/face-analysis")
async def face_analysis(file: UploadFile = File(...)):
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    try:
        result = extract_face_regions(contents)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Face region extraction failed: {str(exc)}",
        )

    return result