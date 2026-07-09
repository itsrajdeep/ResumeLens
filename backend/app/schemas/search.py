"""ResumeAtlas Pydantic Schemas — Search."""
from typing import Any, Optional
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    q: str = Field(..., min_length=1, max_length=500, description="Search query")
    category: Optional[str] = None
    skills: Optional[list[str]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SearchResult(BaseModel):
    id: int
    post_id: int
    category: Optional[str]
    summary: Optional[str]
    skills: list[str] = []
    score: float = 0.0  # relevance score


class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[SearchResult]
