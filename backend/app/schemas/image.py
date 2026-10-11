from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ImageResponse(BaseModel):
    id: str
    assessment_id: str
    view: str
    filename: str
    content_type: str
    file_size: int
    created_at: datetime
    storage_key: Optional[str] = None