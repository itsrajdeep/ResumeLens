"""ResumeAtlas Pydantic Schemas — Resume."""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class SkillOut(BaseModel):
    name: str
    category: Optional[str] = None

    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[list[str]] = None

    model_config = {"from_attributes": True}


class ResumeResponse(BaseModel):
    id: int
    post_id: int
    category: Optional[str] = None
    summary: Optional[str] = None
    anonymous_file_path: Optional[str] = None
    embedding_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # Flattened post fields for frontend cards
    title: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    subreddit: Optional[str] = None
    score: Optional[int] = None
    permalink: Optional[str] = None
    author: Optional[str] = None

    model_config = {"from_attributes": True}


class ResumeDetail(ResumeResponse):
    ocr_text: Optional[str] = None
    parsed_data: Optional[Any] = None
    skills: list[SkillOut] = []
    projects: list[ProjectOut] = []

    model_config = {"from_attributes": True}
