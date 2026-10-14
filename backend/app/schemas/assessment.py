from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class AssessmentCreate(BaseModel):
    """
    Data required to create a new skin assessment session.
    """

    capture_type: str = Field(
        default="upload",
        description="How the assessment images were captured (e.g. upload, camera, or hybrid)."
    )

    capture_modes: Optional[Dict[str, str]] = Field(
        default=None,
        description="Per-view capture method mapping, e.g. {'front': 'camera', 'left': 'upload'}."
    )

    views: List[str] = Field(
        ...,
        description="Facial views provided for the assessment."
    )

    consent_version: Optional[str] = Field(
        default="1.0",
        description="Version of informational assessment consent agreed to by user."
    )

    consented_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when user consented to non-diagnostic informational scan."
    )


class AssessmentRename(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User-assigned custom name for the assessment session."
    )


class AssessmentResponse(BaseModel):
    """
    Basic assessment information returned by the API.
    """

    id: str
    assessment_number: Optional[int] = None
    name: Optional[str] = None
    status: str
    capture_type: str
    capture_modes: Optional[Dict[str, str]] = None
    views: List[str]
    consent_version: Optional[str] = None
    consented_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None