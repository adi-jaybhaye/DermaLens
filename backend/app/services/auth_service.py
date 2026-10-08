from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from bson import ObjectId
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from app.config.database import database
from app.config.settings import settings
from app.schemas.user import UserCreate, UserResponse

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

    # Check if user already exists
    existing = database.users.find_one({"email": email})
    if existing:
        return {"success": False, "reason": "Email is already registered"}

    hashed = hash_password(user_data.password)
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "email": email,
        "password_hash": hashed,
        "full_name": user_data.full_name,
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
            "created_at": now,
        },
    }


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with email and password."""
    email_clean = email.strip().lower()
    user_doc = database.users.find_one({"email": email_clean})
    if not user_doc:
        return None

    if not verify_password(user_doc.get("password_hash", ""), password):
        return None

    return {
        "id": str(user_doc["_id"]),
        "email": user_doc["email"],
        "full_name": user_doc.get("full_name"),
        "created_at": user_doc.get("created_at"),
    }


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch user by MongoDB ObjectId string."""
    if not ObjectId.is_valid(user_id):
        return None
    user_doc = database.users.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        return None
    return {
        "id": str(user_doc["_id"]),
        "email": user_doc["email"],
        "full_name": user_doc.get("full_name"),
        "created_at": user_doc.get("created_at"),
    }
