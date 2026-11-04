from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from bson import ObjectId

from typing import Optional, Dict, Any
from pymongo import ReturnDocument

from app.config.database import database
from app.schemas.assessment import AssessmentCreate
from app.ml.quality.image_quality import check_image_quality
from app.ml.face.face_processor import detect_face, extract_face_regions
from app.ml.skin.skin_analyzer import analyze_skin_regions
from app.ml.xai.gradcam import generate_gradcam
from app.services.storage_service import storage_service


def get_next_assessment_sequence(user_id: Optional[str]) -> int:
    """Atomically increment and return the next sequential assessment number.

    Uses find_one_and_update on user_assessment_sequences collection.
    Guarantees strictly monotonic sequential numbering without race conditions under concurrency
    and prevents duplicate numbering when previous assessments are deleted.
    """
    key = str(user_id) if user_id else "anonymous"

    # For existing accounts before sequence collection initialization:
    # Set initial value to current maximum count if not yet seeded
    existing_seq = database.user_assessment_sequences.find_one({"user_id": key})
    if existing_seq is None:
        existing_count = database.assessment_sessions.count_documents({"user_id": user_id})
        database.user_assessment_sequences.update_one(
            {"user_id": key},
            {"$setOnInsert": {"next_number": existing_count}},
            upsert=True,
        )

    seq_doc = database.user_assessment_sequences.find_one_and_update(
        {"user_id": key},
        {"$inc": {"next_number": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(seq_doc["next_number"])


def create_assessment(data: AssessmentCreate, user_id: str = None) -> str:
    now = datetime.now(timezone.utc)
    consented_at = data.consented_at or now

    # Atomically assign next persistent sequence number
    assessment_number = get_next_assessment_sequence(user_id)
    default_name = f"Assessment {assessment_number}"

    assessment_document = {
        "status": "created",
        "capture_type": data.capture_type,
        "capture_modes": data.capture_modes or {},
        "views": data.views,
        "consent_version": data.consent_version or "1.0",
        "consented_at": consented_at,
        "user_id": user_id,
        "assessment_number": assessment_number,
        "name": default_name,
        "created_at": now,
        "updated_at": now,
    }

    result = database.assessment_sessions.insert_one(
        assessment_document
    )

    return str(result.inserted_id)


def abandon_assessment(assessment_id: str, user_id: Optional[str] = None) -> bool:
    """Mark an incomplete assessment as abandoned and purge partial image artifacts.

    Fail-Safe Storage Abandonment Rule:
    - If storage cleanup fails for ANY biometric image artifact:
      DO NOT delete image records from assessment_images collection.
      DO NOT clear image references from session document.
      Set status = cleanup_pending, store failed_storage_paths and cleanup_error.
      Log critical cleanup error and return False.
    - Image records are deleted and session is marked 'abandoned' ONLY after
      all physical/cloud image storage artifacts are confirmed deleted.
    """
    try:
        object_id = ObjectId(assessment_id)
    except Exception:
        return False

    existing = database.assessment_sessions.find_one({"_id": object_id})
    if not existing:
        return False

    if user_id and existing.get("user_id") and str(existing["user_id"]) != str(user_id):
        return False

    # Completed assessments cannot be abandoned (they must be deleted)
    if existing.get("status") in ("analyzed", "completed"):
        return False

    image_records = list(database.assessment_images.find({"assessment_id": object_id}))
    storage_report = storage_service.delete_assessment_files(existing, image_records)

    # Storage Deletion Integrity Gate for Abandonment
    if not storage_report.get("success", False):
        failed_paths = storage_report.get("failed_paths", [])
        import logging
        logging.getLogger(__name__).critical(
            f"Storage cleanup failed during abandonment of assessment {assessment_id}. "
            f"Failed paths: {failed_paths}. Retaining image metadata to prevent orphaned biometric data."
        )
        database.assessment_sessions.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "status": "cleanup_pending",
                    "cleanup_error": f"Failed to delete {len(failed_paths)} image storage artifact(s) on abandonment",
                    "failed_storage_paths": failed_paths,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        return False

    # Storage cleanup succeeded: purge image records, clear image refs, mark abandoned
    database.assessment_images.delete_many({"assessment_id": object_id})

    now = datetime.now(timezone.utc)
    database.assessment_sessions.update_one(
        {"_id": object_id},
        {"$set": {"status": "abandoned", "images": {}, "updated_at": now}}
    )
    return True


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

    # Ensure persistent assessment_number and name if missing on legacy documents
    if assessment.get("assessment_number") is None:
        user_id = assessment.get("user_id")
        created_time = assessment.get("created_at") or datetime.now(timezone.utc)
        older_count = database.assessment_sessions.count_documents({
            "user_id": user_id,
            "created_at": {"$lt": created_time}
        })
        assessment_number = older_count + 1
        name = assessment.get("name") or f"Assessment {assessment_number}"
        database.assessment_sessions.update_one(
            {"_id": object_id},
            {"$set": {"assessment_number": assessment_number, "name": name}}
        )
        assessment["assessment_number"] = assessment_number
        assessment["name"] = name

    assessment["id"] = str(assessment.pop("_id"))

    return assessment


def get_assessment_history(user_id: str = None):
    # Isolated by identity; unauthenticated requests only see anonymous sessions
    query = {"user_id": user_id}
    assessments = list(database.assessment_sessions.find(
        query,
        {
            "_id": 1,
            "status": 1,
            "capture_type": 1,
            "capture_modes": 1,
            "views": 1,
            "user_id": 1,
            "assessment_number": 1,
            "name": 1,
            "created_at": 1,
            "updated_at": 1,
        },
    ).sort("created_at", -1))

    # Check if any legacy assessments are missing persistent assessment_number
    missing_numbers = [a for a in assessments if a.get("assessment_number") is None]
    if missing_numbers:
        # Sort chronologically ascending to assign stable sequential numbers
        chrono = sorted(assessments, key=lambda a: a.get("created_at") or datetime.min)
        for idx, a in enumerate(chrono, start=1):
            if a.get("assessment_number") is None:
                a["assessment_number"] = idx
                if not a.get("name"):
                    a["name"] = f"Assessment {idx}"
                database.assessment_sessions.update_one(
                    {"_id": a["_id"]},
                    {"$set": {"assessment_number": idx, "name": a["name"]}}
                )

    results = []
    for assessment in assessments:
        assessment["id"] = str(assessment.pop("_id"))
        if not assessment.get("name"):
            assessment["name"] = f"Assessment {assessment.get('assessment_number', 1)}"
        results.append(assessment)

    return results


def rename_assessment(assessment_id: str, new_name: str, user_id: str = None) -> bool:
    """Optionally rename an assessment session with identity/ownership safety."""
    try:
        object_id = ObjectId(assessment_id)
    except Exception:
        return False

    existing = database.assessment_sessions.find_one({"_id": object_id})
    if not existing:
        return False

    if user_id and existing.get("user_id") and str(existing["user_id"]) != str(user_id):
        return False

    clean_name = new_name.strip()
    if not clean_name:
        return False

    res = database.assessment_sessions.update_one(
        {"_id": object_id},
        {"$set": {"name": clean_name, "updated_at": datetime.now(timezone.utc)}}
    )
    return res.acknowledged


def delete_assessment(assessment_id: str, user_id: str = None) -> bool:
    """Delete an assessment session, all associated physical image files, and database records.

    Fail-Safe Biometric Storage Rule:
    - If storage deletion fails for ANY biometric image artifact:
      DO NOT delete database records.
      Update session status to 'cleanup_pending' with failed file paths.
      Log critical error and return False.
    - Database records are ONLY purged once all physical/cloud image artifacts are verified deleted.
    """
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

    # 1. Clean up physical image files from session document & assessment_images collection
    image_records = list(database.assessment_images.find({"assessment_id": object_id}))
    storage_report = storage_service.delete_assessment_files(existing, image_records)

    # 2. Storage Deletion Integrity Gate
    if not storage_report.get("success", False):
        failed_paths = storage_report.get("failed_paths", [])
        import logging
        logging.getLogger(__name__).critical(
            f"Storage cleanup failed for assessment {assessment_id}. "
            f"Failed paths: {failed_paths}. Retaining database records to prevent orphaned biometric data."
        )
        database.assessment_sessions.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "status": "cleanup_pending",
                    "cleanup_error": f"Failed to delete {len(failed_paths)} image storage artifact(s)",
                    "failed_storage_paths": failed_paths,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        return False

    # 3. Purge database records only after storage cleanup is confirmed
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
        if not file_path:
            continue

        try:
            image_bytes = storage_service.read_file(file_path)
        except Exception:
            continue

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