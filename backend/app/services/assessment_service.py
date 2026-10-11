from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from bson import ObjectId

from app.config.database import database
from app.schemas.assessment import AssessmentCreate
from app.ml.quality.image_quality import check_image_quality
from app.ml.face.face_processor import detect_face, extract_face_regions
from app.ml.skin.skin_analyzer import analyze_skin_regions
from app.ml.xai.gradcam import generate_gradcam


def create_assessment(data: AssessmentCreate, user_id: str = None) -> str:
    now = datetime.now(timezone.utc)
    consented_at = data.consented_at or now

    assessment_document = {
        "status": "created",
        "capture_type": data.capture_type,
        "capture_modes": data.capture_modes or {},
        "views": data.views,
        "consent_version": data.consent_version or "1.0",
        "consented_at": consented_at,
        "user_id": user_id,
        "created_at": now,
        "updated_at": now,
    }

    result = database.assessment_sessions.insert_one(
        assessment_document
    )

    return str(result.inserted_id)


def get_assessment(assessment_id: str):
    try:
        object_id = ObjectId(assessment_id)
    except Exception:
        return None

    assessment = database.assessment_sessions.find_one(
        {"_id": object_id}
    )

    if assessment is None:
        return None

    assessment["id"] = str(assessment.pop("_id"))

    return assessment


def get_assessment_history(user_id: str = None):
    # Isolated by identity; unauthenticated requests only see anonymous sessions
    query = {"user_id": user_id}
    assessments = database.assessment_sessions.find(
        query,
        {
            "_id": 1,
            "status": 1,
            "capture_type": 1,
            "views": 1,
            "user_id": 1,
            "created_at": 1,
            "updated_at": 1,
        },
    ).sort("created_at", -1)

    results = []

    for assessment in assessments:
        assessment["id"] = str(assessment.pop("_id"))
        results.append(assessment)

    return results


def delete_assessment(assessment_id: str, user_id: str = None) -> bool:
    """Delete an assessment session, all associated physical image files, and database records."""
    try:
        object_id = ObjectId(assessment_id)
    except Exception:
        return False

    existing = database.assessment_sessions.find_one({"_id": object_id})
    if not existing:
        return False

    # Check ownership: if session has a user_id and it doesn't match, reject
    if user_id and existing.get("user_id") and str(existing["user_id"]) != str(user_id):
        return False

    # 1. Clean up physical image files from session document
    images = existing.get("images", {})
    for view_name, view_data in images.items():
        file_path_str = view_data.get("file_path")
        if file_path_str:
            try:
                p = Path(file_path_str)
                if p.exists() and p.is_file():
                    p.unlink()
            except Exception:
                pass

    # 2. Clean up any physical files recorded in assessment_images collection
    image_records = database.assessment_images.find({"assessment_id": object_id})
    for img_rec in image_records:
        rec_path_str = img_rec.get("file_path")
        if rec_path_str:
            try:
                p = Path(rec_path_str)
                if p.exists() and p.is_file():
                    p.unlink()
            except Exception:
                pass

    # 3. Delete database records
    database.assessment_images.delete_many({"assessment_id": object_id})
    result = database.assessment_sessions.delete_one({"_id": object_id})

    return result.deleted_count > 0


def process_assessment_image(
    assessment_id: str,
    image_bytes: bytes,
    view: str,
    file_path: str = None,
):
    # --------------------------------------------------------
    # 1. Image Quality Check
    # --------------------------------------------------------

    quality = check_image_quality(image_bytes)

    if not quality["valid"]:
        return {
            "success": False,
            "stage": "quality_check",
            "quality": quality,
        }

    # --------------------------------------------------------
    # 2. Strict Single Face Gate (Zero or Multiple Faces Rejected)
    # --------------------------------------------------------

    face_detection = detect_face(image_bytes)

    if not face_detection or not face_detection.get("success"):
        return {
            "success": False,
            "stage": "face_detection",
            "message": (
                face_detection.get("reason", "Face detection failed")
                if face_detection
                else "Face detection failed"
            ),
            "face_count": face_detection.get("face_count", 0) if face_detection else 0,
            "quality": quality,
        }

    # --------------------------------------------------------
    # 3. Facial Landmark Mesh & 5-Region Extraction
    # --------------------------------------------------------

    face_result = extract_face_regions(image_bytes)

    if not face_result.get("success"):
        return {
            "success": False,
            "stage": "landmark_extraction",
            "message": face_result.get(
                "reason",
                "Facial region extraction failed",
            ),
            "quality": quality,
        }

    regions = face_result["regions"]

    # --------------------------------------------------------
    # 3. EfficientNet-B0 Skin Analysis
    # --------------------------------------------------------

    skin_result = analyze_skin_regions(
        image_bytes=image_bytes,
        regions=regions,
    )

    if not skin_result.get("success"):
        return {
            "success": False,
            "stage": "skin_analysis",
            "message": skin_result.get(
                "reason",
                "Skin analysis failed",
            ),
            "quality": quality,
            "regions": regions,
        }

    # --------------------------------------------------------
    # 4. Store Complete Analysis Result
    # --------------------------------------------------------

    update_fields = {
        f"images.{view}.quality": quality,
        f"images.{view}.face_regions": regions,
        f"images.{view}.skin_analysis": skin_result,
        f"images.{view}.analysis_completed": True,
        "status": "processed",
        "updated_at": datetime.now(timezone.utc),
    }

    if file_path:
        update_fields[f"images.{view}.file_path"] = file_path

    database.assessment_sessions.update_one(
        {"_id": ObjectId(assessment_id)},
        {"$set": update_fields},
    )

    # --------------------------------------------------------
    # 5. Return Complete Result
    # --------------------------------------------------------

    return {
        "success": True,
        "view": view,
        "quality": quality,
        "face_regions": regions,
        "skin_analysis": skin_result,
    }


def analyze_assessment(assessment_id: str) -> dict:
    """Run XAI (Grad-CAM) on all processed views of an assessment.

    Generates per-region Grad-CAM heatmaps and stores the results
    in the assessment document.
    """
    try:
        object_id = ObjectId(assessment_id)
    except Exception:
        return {
            "success": False,
            "reason": "Invalid assessment ID",
        }

    assessment = database.assessment_sessions.find_one(
        {"_id": object_id}
    )

    if assessment is None:
        return {
            "success": False,
            "reason": "Assessment not found",
        }

    images = assessment.get("images", {})

    if not images:
        return {
            "success": False,
            "reason": "No images have been uploaded yet",
        }

    xai_results = {}
    update_fields = {}

    for view_name, view_data in images.items():

        if not view_data.get("analysis_completed"):
            continue

        file_path = view_data.get("file_path")

        if not file_path or not Path(file_path).exists():
            continue

        # Load original image
        image_bytes = Path(file_path).read_bytes()

        # Get stored region coordinates
        face_regions = view_data.get("face_regions", {})
        skin_analysis = view_data.get("skin_analysis", {})
        region_results = skin_analysis.get("regions", {})

        view_xai = {}

        for region_name, region_coords in face_regions.items():

            region_data = region_results.get(region_name, {})

            if not region_data.get("valid", False):
                continue

            # Crop the region from the original image
            try:
                image_array = np.frombuffer(
                    image_bytes, dtype=np.uint8
                )
                image = cv2.imdecode(
                    image_array, cv2.IMREAD_COLOR
                )

                x = max(0, int(region_coords["x"]))
                y = max(0, int(region_coords["y"]))
                w = int(region_coords["width"])
                h = int(region_coords["height"])
                x2 = min(image.shape[1], x + w)
                y2 = min(image.shape[0], y + h)

                roi = image[y:y2, x:x2]

                if roi.size == 0:
                    continue

                success, encoded = cv2.imencode(
                    ".jpg", roi
                )
                if not success:
                    continue

                region_bytes = encoded.tobytes()

                # Generate Grad-CAM for this region crop
                gradcam_result = generate_gradcam(
                    region_bytes
                )

                if gradcam_result.get("success"):
                    view_xai[region_name] = {
                        "predicted_concern": (
                            gradcam_result["predicted_concern"]
                        ),
                        "confidence": (
                            gradcam_result["confidence"]
                        ),
                        "heatmap_base64": (
                            gradcam_result["heatmap_base64"]
                        ),
                        "overlay_base64": (
                            gradcam_result["overlay_base64"]
                        ),
                    }

            except Exception:
                # Skip regions that fail XAI generation
                continue

        if view_xai:
            xai_results[view_name] = view_xai
            update_fields[f"images.{view_name}.xai"] = view_xai

    if not xai_results:
        return {
            "success": False,
            "reason": (
                "No regions could be processed for XAI. "
                "Ensure images have been uploaded and analysed."
            ),
        }

    # Store XAI results and update status
    update_fields["status"] = "analyzed"
    update_fields["updated_at"] = datetime.now(timezone.utc)

    database.assessment_sessions.update_one(
        {"_id": object_id},
        {"$set": update_fields},
    )

    return {
        "success": True,
        "assessment_id": assessment_id,
        "xai": xai_results,
    }