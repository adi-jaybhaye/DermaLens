from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId

from app.config.database import database
from app.services.knowledge_service import (
    get_concern,
    get_safety_disclaimer,
    build_why_identified,
)
from app.api.deps import get_current_user, verify_assessment_ownership


router = APIRouter()


@router.get("/assessments/{assessment_id}/results")
def get_assessment_results(
    assessment_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Return structured assessment results with knowledge enrichment,
    safety disclaimers, and ownership verification.
    """

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

    images = assessment.get("images", {})
    result_views = {}

    for view, image_data in images.items():

        skin_analysis = image_data.get("skin_analysis", {})
        regions_raw = skin_analysis.get("regions", {})

        enriched_regions = {}

        for region_name, region_data in regions_raw.items():

            if not region_data.get("valid", False):
                enriched_regions[region_name] = {
                    "valid": False,
                    "reason": region_data.get(
                        "reason", "Invalid region"
                    ),
                }
                continue

            ml_pred = region_data.get("ml_prediction", {})
            predicted = ml_pred.get("predicted_concern")
            confidence = ml_pred.get("confidence", 0.0)

            # Knowledge enrichment
            concern_info = None
            why_identified = None
            why_it_can_occur = None
            visual_evidence = None
            sources = []

            if predicted and ml_pred.get("success"):
                knowledge = get_concern(predicted)

                if knowledge:
                    concern_info = {
                        "concept": knowledge["concept"],
                        "display_name": knowledge["display_name"],
                        "description": knowledge["description"],
                    }
                    why_it_can_occur = knowledge["why_it_can_occur"]
                    visual_evidence = (
                        knowledge["visual_characteristics"]
                    )
                    sources = knowledge["evidence_references"]

                is_confident = ml_pred.get("is_confident", confidence >= 0.35)
                confidence_status = ml_pred.get(
                    "confidence_status",
                    "possible_pattern" if is_confident else "insufficient_confidence",
                )

                if is_confident:
                    why_identified = build_why_identified(
                        region_name=region_name,
                        predicted_concern=predicted,
                        confidence=confidence,
                    )
                else:
                    why_identified = (
                        f"Visual analysis identified weak features for {concern_info['display_name'] if concern_info else predicted} "
                        f"in the {region_name.replace('_', ' ')} region with low confidence ({round(confidence * 100, 1)}%), "
                        f"which is below the certainty threshold. This is considered an inconclusive pattern."
                    )

            enriched_regions[region_name] = {
                "valid": True,
                "concern": {
                    "concept": predicted,
                    "display_name": (
                        concern_info["display_name"]
                        if concern_info
                        else predicted
                    ),
                    "confidence": confidence,
                    "is_confident": ml_pred.get("is_confident", confidence >= 0.35),
                    "confidence_status": ml_pred.get("confidence_status", "possible_pattern"),
                    "why_identified": why_identified,
                    "why_it_can_occur": why_it_can_occur,
                    "visual_evidence": visual_evidence,
                    "sources": sources,
                } if predicted else None,
                "all_probabilities": ml_pred.get(
                    "probabilities", {}
                ),
                "texture_metrics": {
                    "mean_brightness": region_data.get(
                        "mean_brightness"
                    ),
                    "brightness_std": region_data.get(
                        "brightness_std"
                    ),
                    "texture_variance": region_data.get(
                        "texture_variance"
                    ),
                },
            }

        # XAI data (present if analyze endpoint was called)
        xai_data = image_data.get("xai")

        result_views[view] = {
            "analysis_completed": image_data.get(
                "analysis_completed", False
            ),
            "quality": image_data.get("quality"),
            "regions": enriched_regions,
            "xai": xai_data,
        }

    # Skin type — not available without a validated model
    skin_type = {
        "status": "unavailable",
        "note": (
            "Skin type determination requires physical sebum "
            "measurement and barrier evaluation. DermaLens focuses on "
            "8 visible surface skin patterns."
        ),
    }

    return {
        "assessment_id": assessment_id,
        "status": assessment.get("status"),
        "capture_type": assessment.get("capture_type"),
        "skin_type": skin_type,
        "views": result_views,
        "safety": get_safety_disclaimer(),
    }