from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.settings import settings
from app.services.auth_service import decode_access_token, get_user_by_id

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """Require an authenticated user via Bearer token or secure HttpOnly session cookie."""
    token: Optional[str] = None

    # 1. Check Authorization Bearer header
    if credentials and credentials.credentials:
        token = credentials.credentials
    # 2. Fall back to secure HttpOnly session cookie
    elif request and request.cookies.get(settings.cookie_name):
        token = request.cookies.get(settings.cookie_name)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """Return the authenticated user if Bearer token or session cookie is provided, else None."""
    token: Optional[str] = None

    if credentials and credentials.credentials:
        token = credentials.credentials
    elif request and request.cookies.get(settings.cookie_name):
        token = request.cookies.get(settings.cookie_name)

    if not token:
        return None

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None

    return get_user_by_id(payload["sub"])


def verify_assessment_ownership(
    assessment: Dict[str, Any],
    user: Dict[str, Any],
) -> None:
    """Ensure the authenticated user is the legitimate owner of the assessment.

    Raises 403 Forbidden if the user does not own the assessment.
    """
    owner_id = assessment.get("user_id")
    if not owner_id or str(owner_id) != str(user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not have permission to access this assessment",
        )
