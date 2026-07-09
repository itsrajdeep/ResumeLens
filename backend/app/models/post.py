"""
Post model — Represents a Reddit post containing a resume.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime
)
from sqlalchemy.orm import relationship
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reddit_id = Column(String(20), unique=True, nullable=False, index=True)
    subreddit = Column(String(50), nullable=False, index=True)
    title = Column(Text, nullable=False)
    author = Column(String(50))
    score = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False)
    permalink = Column(Text)
    file_url = Column(Text)
    file_type = Column(String(10))  # pdf, png, jpg, jpeg
    processed = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    last_checked = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post(reddit_id={self.reddit_id}, subreddit={self.subreddit})>"
