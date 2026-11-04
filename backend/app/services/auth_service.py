import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from bson import ObjectId
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from pymongo.errors import PyMongoError

from app.config.database import database
from app.config.settings import settings
from app.schemas.user import UserCreate, UserResponse

logger = logging.getLogger(__name__)
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    return ph.hash(password)


def verify_password(password_hash: str, candidate_password: str) -> bool:
    """Verify candidate password against Argon2id hash."""
    try:
        return ph.verify(password_hash, candidate_password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def create_access_token(
    user_id: str,
    email: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return token


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token.
    
    Returns payload dict if valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.PyJWTError:
        return None


def register_user(user_data: UserCreate) -> Dict[str, Any]:
    """Register a new user in MongoDB users collection."""
    email = user_data.email.strip().lower()

    try:
        # Check if user already exists
        existing = database.users.find_one({"email": email})
        if existing:
            return {"success": False, "reason": "Email is already registered"}

        hashed = hash_password(user_data.password)
        now = datetime.now(timezone.utc).isoformat()
        consent_version = user_data.consent_version or "1.0"

        doc = {
            "email": email,
            "password_hash": hashed,
            "full_name": user_data.full_name,
            "consent_version": consent_version,
            "consented_at": now,
            "created_at": now,
            "updated_at": now,
            "is_active": True,
        }

        result = database.users.insert_one(doc)
        user_id = str(result.inserted_id)

        return {
            "success": True,
            "user": {
                "id": user_id,
                "email": email,
                "full_name": user_data.full_name,
                "consent_version": consent_version,
                "consented_at": now,
                "created_at": now,
            },
        }
    except PyMongoError as e:
        logger.error(f"Database error during registration: {e}")
        return {"success": False, "reason": "Database connection error. Please try again later."}


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with email and password."""
    email_clean = email.strip().lower()
    try:
        user_doc = database.users.find_one({"email": email_clean})
    except PyMongoError as e:
        logger.error(f"Database error during authentication: {e}")
        raise

    if not user_doc:
        return None

    if not user_doc.get("is_active", True):
        return None

    if not verify_password(user_doc.get("password_hash", ""), password):
        return None

    return {
        "id": str(user_doc["_id"]),
        "email": user_doc["email"],
        "full_name": user_doc.get("full_name"),
        "consent_version": user_doc.get("consent_version"),
        "consented_at": user_doc.get("consented_at"),
        "created_at": user_doc.get("created_at"),
        "is_active": user_doc.get("is_active", True),
    }


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch user by MongoDB ObjectId string."""
    if not ObjectId.is_valid(user_id):
        return None
    try:
        user_doc = database.users.find_one({"_id": ObjectId(user_id)})
    except PyMongoError as e:
        logger.error(f"Database error during get_user_by_id: {e}")
        return None

    if not user_doc:
        return None
    if not user_doc.get("is_active", True):
        return None
    return {
        "id": str(user_doc["_id"]),
        "email": user_doc["email"],
        "full_name": user_doc.get("full_name"),
        "consent_version": user_doc.get("consent_version"),
        "consented_at": user_doc.get("consented_at"),
        "created_at": user_doc.get("created_at"),
        "is_active": user_doc.get("is_active", True),
    }


def delete_user_account(user_id: str) -> Dict[str, Any]:
    """Permanently delete user account and wipe all associated assessments and image files.

    Fail-Safe Biometric Account Deletion Rule:
    - Calls delete_assessment() for each assessment belonging to this user.
    - If ANY assessment storage cleanup fails:
      DO NOT delete the user account record.
      DO NOT claim permanent deletion succeeded.
      Retain user account and the affected assessment(s) in cleanup_pending state.
      Return controlled failure response to allow cleanup retry.
    - User record is deleted ONLY after ALL associated assessments and biometric
      storage artifacts have been confirmed purged.
    """
    if not ObjectId.is_valid(user_id):
        return {"success": False, "reason": "Invalid user ID"}

    user_obj_id = ObjectId(user_id)
    try:
        user_doc = database.users.find_one({"_id": user_obj_id})
        if not user_doc:
            return {"success": False, "reason": "User not found"}

        from app.services.assessment_service import delete_assessment

        # Find all assessments belonging to this user
        assessments = list(database.assessment_sessions.find({"user_id": str(user_id)}))
        failed_assessment_ids = []
        for assessment in assessments:
            assessment_id = str(assessment["_id"])
            success = delete_assessment(assessment_id, user_id=str(user_id))
            if not success:
                failed_assessment_ids.append(assessment_id)

        if failed_assessment_ids:
            logger.critical(
                f"Account deletion blocked for user {user_id}: "
                f"Biometric storage cleanup failed for assessment(s) {failed_assessment_ids}. "
                "Retaining user account and assessment records to prevent orphaned biometric data."
            )
            return {
                "success": False,
                "reason": (
                    f"Biometric data cleanup failed for {len(failed_assessment_ids)} assessment(s). "
                    "User account retained to prevent orphaned records. Retry deletion after resolving storage issues."
                ),
                "failed_assessments": failed_assessment_ids,
            }

        # Delete user record ONLY after all assessments and storage artifacts are confirmed deleted
        result = database.users.delete_one({"_id": user_obj_id})
        if result.deleted_count == 0:
            return {"success": False, "reason": "Failed to delete user record from database"}

        return {"success": True, "message": "Account and all associated biometric data permanently deleted"}
    except PyMongoError as e:
        logger.error(f"Database error during account deletion: {e}")
        return {"success": False, "reason": "Database connection error. Please try again later."}

