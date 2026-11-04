import logging
from fastapi import APIRouter, HTTPException, Depends, Request, Response, status
from app.config.settings import settings
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
    delete_user_account,
)
from app.api.deps import get_current_user
from app.utils.rate_limiter import auth_limiter

logger = logging.getLogger(__name__)
router = APIRouter()


def _set_auth_cookie(response: Response, token: str) -> None:
    is_prod = settings.environment.lower() == "production"
    cookie_max_age = settings.jwt_access_token_expire_minutes * 60
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        max_age=cookie_max_age,
        expires=cookie_max_age,
        httponly=True,
        secure=is_prod,
        samesite=settings.cookie_samesite,
        path="/",
    )


def _clear_auth_cookie(response: Response) -> None:
    is_prod = settings.environment.lower() == "production"
    response.delete_cookie(
        key=settings.cookie_name,
        path="/",
        httponly=True,
        secure=is_prod,
        samesite=settings.cookie_samesite,
    )


@router.post("/auth/register", response_model=TokenResponse)
def register(user_data: UserCreate, request: Request, response: Response):
    """Register a new user account with Argon2id password hashing and set HttpOnly session cookie."""
    auth_limiter.check(request)

    result = register_user(user_data)
    if not result.get("success"):
        reason = result.get("reason", "Registration failed")
        status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
            if "database" in reason.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code,
            detail=reason,
        )

    user = result["user"]
    token = create_access_token(user_id=user["id"], email=user["email"])
    _set_auth_cookie(response, token)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(**user),
    )


@router.post("/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin, request: Request, response: Response):
    """Authenticate user credentials, set HttpOnly session cookie, and return signed JWT."""
    auth_limiter.check(request)

    try:
        user = authenticate_user(
            email=credentials.email,
            password=credentials.password,
        )
    except Exception as exc:
        logger.error(f"Authentication database exception: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable. Please try again.",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user_id=user["id"], email=user["email"])
    _set_auth_cookie(response, token)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(**user),
    )


@router.post("/auth/logout")
def logout(response: Response):
    """Log out user by clearing the secure HttpOnly session cookie."""
    _clear_auth_cookie(response)
    return {"message": "Logged out successfully"}


@router.get("/auth/me", response_model=UserResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    """Return profile of currently authenticated user."""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        consent_version=current_user.get("consent_version"),
        consented_at=current_user.get("consented_at"),
        created_at=current_user.get("created_at"),
    )


@router.delete("/auth/me")
def delete_account(response: Response, current_user: dict = Depends(get_current_user)):
    """Permanently delete user account, clear session cookie, and wipe all associated biometric assessment data."""
    result = delete_user_account(current_user["id"])
    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("reason", "Failed to completely purge user account and biometric data"),
        )
    _clear_auth_cookie(response)
    return {"message": "Account and all associated biometric records permanently deleted"}
