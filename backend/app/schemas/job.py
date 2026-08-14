from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class JobCreateRequest(BaseModel):
    operation: str
    input_file_id: Optional[int] = None
    input_file_ids: Optional[List[int]] = None
    options: Dict[str, Any] = {}


class JobOut(BaseModel):
    id: int
    operation: str
    status: str
    progress: int
    error_message: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)