from datetime import datetime

from pydantic import BaseModel


class ImageResponse(BaseModel):
    id: str
    assessment_id: str
    view: str
    filename: str
    content_type: str
    file_size: int
    file_path: str
    created_at: datetime