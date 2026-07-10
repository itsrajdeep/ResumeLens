"""ResumeAtlas Pydantic Schemas — Search."""
from typing import Optional
from pydantic import BaseModel


class SearchResult(BaseModel):
    id: int
    post_id: Optional[int] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    skills: list[str] = []
    score: float = 0.0


class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[SearchResult]
