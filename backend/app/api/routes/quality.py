from fastapi import APIRouter, File, HTTPException, UploadFile

from app.ml.quality.image_quality import check_image_quality


router = APIRouter()


@router.post("/quality-check")
async def quality_check(
    file: UploadFile = File(...),
):
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Image file is empty",
        )

    result = check_image_quality(contents)

    return result