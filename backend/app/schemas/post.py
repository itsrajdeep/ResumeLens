"""
Post schemas — Request/response models for Reddit posts.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PostBase(BaseModel):
    reddit_id: str
    subreddit: str
    title: str
    author: Optional[str] = None
    score: int = 0
    created_at: datetime
    permalink: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None


class PostResponse(PostBase):
    """Schema for post API responses."""
    id: int
    processed: bool
    deleted: bool
    last_checked: Optional[datetime] = None

    model_config = {"from_attributes": True}
