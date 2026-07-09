"""ResumeAtlas Pydantic Schemas — Resume."""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class ResumeBase(BaseModel):
    raw_file_path: str
    file_hash: str
    category: Optional[str] = None
    summary: Optional[str] = None


class ResumeResponse(ResumeBase):
    id: int
    post_id: int
    anonymous_file_path: Optional[str] = None
    embedding_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeDetail(ResumeResponse):
    ocr_text: Optional[str] = None
    parsed_data: Optional[Any] = None
