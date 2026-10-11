import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, status
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
from app.api.deps import get_current_user, verify_assessment_ownership
from app.utils.rate_limiter import api_limiter

logger = logging.getLogger(__name__)
router = APIRouter()


# ----------------------------------------------------------------
# Fixed-path routes MUST come before parameterised routes so that
# FastAPI does not capture e.g. "history" as an {assessment_id}.
# ----------------------------------------------------------------


@router.get("/assessments/history")
def list_assessment_history(
    current_user: dict = Depends(get_current_user),
):
    """Return a summary list of assessments for the authenticated user, newest first."""
    return get_assessment_history(user_id=current_user["id"])


@router.post("/assessments")
def create_new_assessment(
    data: AssessmentCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new private assessment session owned by the authenticated user."""
    try:
        assessment_id = create_assessment(data, user_id=current_user["id"])

        return {
            "message": "Assessment created successfully",
            "assessment_id": assessment_id,
            "status": "created",
        }

    except Exception as e:
        logger.error(f"Failed to create assessment: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create assessment. Please try again.",
        )


@router.get("/assessments/{assessment_id}")
def get_existing_assessment(
    assessment_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Retrieve an assessment record with ownership verification."""
    if not ObjectId.is_valid(assessment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assessment ID",
        )

    assessment = get_assessment(assessment_id)

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    verify_assessment_ownership(assessment, current_user)
    return assessment


@router.delete("/assessments/{assessment_id}")
def remove_assessment(
    assessment_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete an assessment and its associated physical images with ownership verification."""
    if not ObjectId.is_valid(assessment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assessment ID",
        )

    assessment = get_assessment(assessment_id)
    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    verify_assessment_ownership(assessment, current_user)

    deleted = delete_assessment(assessment_id, user_id=current_user["id"])
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete assessment session",
        )

    return {
        "message": "Assessment deleted successfully",
        "assessment_id": assessment_id,
    }


@router.get("/assessments/{assessment_id}/status")
def get_status(
    assessment_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Return the processing status of an assessment with ownership verification."""
    if not ObjectId.is_valid(assessment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assessment ID",
        )

    assessment = database.assessment_sessions.find_one(
        {"_id": ObjectId(assessment_id)}
    )

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    verify_assessment_ownership(assessment, current_user)

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
def trigger_analysis(
    assessment_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """Run XAI (Grad-CAM) and knowledge enrichment with ownership verification and rate limiting."""
    api_limiter.check(request)

    if not ObjectId.is_valid(assessment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assessment ID",
        )

    assessment = database.assessment_sessions.find_one(
        {"_id": ObjectId(assessment_id)}
    )

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    verify_assessment_ownership(assessment, current_user)

    try:
        result = analyze_assessment(assessment_id)

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get(
                    "reason",
                    "Analysis failed",
                ),
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        logger.error(f"Analysis failed for assessment {assessment_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Assessment analysis failed. Please try again.",
        )