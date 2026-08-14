from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class UploadURLRequest(BaseModel):
    filename: str
    content_type: str
    size: int


class UploadURLResponse(BaseModel):
    upload_url: str
    file_id: int
    storage_key: str


class FileOut(BaseModel):
    id: int
    filename: str
    mime_type: str
    extension: Optional[str]
    size: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)