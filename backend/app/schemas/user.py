from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: Optional[str] = Field(None, max_length=100, description="User full name")
    consent_version: Optional[str] = Field("1.0", description="Privacy and terms consent version")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v


class UserLogin(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    consent_version: Optional[str] = None
    consented_at: Optional[str] = None
    created_at: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
