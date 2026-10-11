from fastapi import APIRouter, File, HTTPException, UploadFile, Request

from app.ml.quality.image_quality import check_image_quality
from app.utils.rate_limiter import upload_limiter


router = APIRouter()


@router.post("/quality-check")
async def quality_check(
    request: Request,
    file: UploadFile = File(...),
):
    upload_limiter.check(request)
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Image file is empty",
        )

    result = check_image_quality(contents)

    return result