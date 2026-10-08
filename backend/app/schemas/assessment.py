from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AssessmentCreate(BaseModel):
    """
    Data required to create a new skin assessment session.
    """

    capture_type: str = Field(
        ...,
        description="How the assessment images were captured."
    )

    views: List[str] = Field(
        ...,
        description="Facial views provided for the assessment."
    )


class AssessmentResponse(BaseModel):
    """
    Basic assessment information returned by the API.
    """

    id: str
    status: str
    capture_type: str
    views: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None