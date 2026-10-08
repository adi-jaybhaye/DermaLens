from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId

from app.config.database import database
from app.schemas.assessment import AssessmentCreate
from app.services.assessment_service import (
    create_assessment,
    get_assessment,
    get_assessment_history,
    delete_assessment,
    analyze_assessment,
)
from app.api.deps import get_optional_current_user

router = APIRouter()


# ----------------------------------------------------------------
# Fixed-path routes MUST come before parameterised routes so that
# FastAPI does not capture e.g. "history" as an {assessment_id}.
# ----------------------------------------------------------------


@router.get("/assessments/history")
def list_assessment_history(
    user: Optional[dict] = Depends(get_optional_current_user),
):
    """Return a summary list of assessments, newest first.
    Filters by authenticated user if logged in.
    """
    user_id = user["id"] if user else None
    return get_assessment_history(user_id=user_id)


@router.post("/assessments")
def create_new_assessment(
    data: AssessmentCreate,
    user: Optional[dict] = Depends(get_optional_current_user),
):
    try:
        user_id = user["id"] if user else None
        assessment_id = create_assessment(data, user_id=user_id)

        return {
            "message": "Assessment created successfully",
            "assessment_id": assessment_id,
            "status": "created",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/assessments/{assessment_id}")
def get_existing_assessment(assessment_id: str):

    if not ObjectId.is_valid(assessment_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid assessment ID",
        )

    assessment = get_assessment(assessment_id)

    if assessment is None:
        raise HTTPException(
            status_code=404,
            detail="Assessment not found",
        )

    return assessment


@router.delete("/assessments/{assessment_id}")
def remove_assessment(
    assessment_id: str,
    user: Optional[dict] = Depends(get_optional_current_user),
):
    """Delete an assessment and its associated data."""

    if not ObjectId.is_valid(assessment_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid assessment ID",
        )

    user_id = user["id"] if user else None
    deleted = delete_assessment(assessment_id, user_id=user_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Assessment not found or access denied",
        )

    return {
        "message": "Assessment deleted successfully",
        "assessment_id": assessment_id,
    }


@router.get("/assessments/{assessment_id}/status")
def get_status(assessment_id: str):
    """Return the processing status of an assessment."""

    if not ObjectId.is_valid(assessment_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid assessment ID",
        )

    assessment = database.assessment_sessions.find_one(
        {"_id": ObjectId(assessment_id)},
        {
            "_id": 0,
            "status": 1,
            "views": 1,
            "images": 1,
            "created_at": 1,
            "updated_at": 1,
        },
    )

    if assessment is None:
        raise HTTPException(
            status_code=404,
            detail="Assessment not found",
        )

    # Compute per-view completion
    images = assessment.get("images", {})
    views_status = {}

    for view_name, view_data in images.items():
        views_status[view_name] = {
            "analysis_completed": view_data.get(
                "analysis_completed", False
            ),
            "has_file": bool(view_data.get("file_path")),
        }

    return {
        "assessment_id": assessment_id,
        "status": assessment.get("status", "unknown"),
        "requested_views": assessment.get("views", []),
        "processed_views": views_status,
        "created_at": assessment.get("created_at"),
        "updated_at": assessment.get("updated_at"),
    }


@router.post("/assessments/{assessment_id}/analyze")
def trigger_analysis(assessment_id: str):
    """Run XAI (Grad-CAM) and knowledge enrichment on processed views.

    This endpoint should be called after images have been uploaded
    and the initial skin analysis is complete.
    """

    if not ObjectId.is_valid(assessment_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid assessment ID",
        )

    try:
        result = analyze_assessment(assessment_id)

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get(
                    "reason",
                    "Analysis failed",
                ),
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(exc)}",
        )