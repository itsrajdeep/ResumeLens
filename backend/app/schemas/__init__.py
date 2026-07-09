"""ResumeAtlas Pydantic Schemas."""
from app.schemas.post import PostBase, PostResponse
from app.schemas.resume import ResumeBase, ResumeResponse, ResumeDetail
from app.schemas.search import SearchQuery, SearchResult, SearchResponse

__all__ = [
    "PostBase", "PostResponse",
    "ResumeBase", "ResumeResponse", "ResumeDetail",
    "SearchQuery", "SearchResult", "SearchResponse",
]
