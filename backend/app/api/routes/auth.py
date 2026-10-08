from fastapi import APIRouter, HTTPException, Depends, Request, status
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_access_token,
)
from app.api.deps import get_current_user
from app.utils.rate_limiter import auth_limiter

router = APIRouter()


@router.post("/auth/register", response_model=TokenResponse)
def register(user_data: UserCreate, request: Request):
    """Register a new user account with Argon2id password hashing."""
    auth_limiter.check(request)

    result = register_user(user_data)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("reason", "Registration failed"),
        )

    user = result["user"]
    token = create_access_token(user_id=user["id"], email=user["email"])

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(**user),
    )


@router.post("/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin, request: Request):
    """Authenticate user credentials and return signed JWT."""
    auth_limiter.check(request)

    user = authenticate_user(
        email=credentials.email,
        password=credentials.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user_id=user["id"], email=user["email"])

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(**user),
    )


@router.post("/auth/logout")
def logout():
    """Client-side token disposal endpoint."""
    return {"message": "Logged out successfully"}


@router.get("/auth/me", response_model=UserResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    """Return profile of currently authenticated user."""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        created_at=current_user.get("created_at"),
    )
