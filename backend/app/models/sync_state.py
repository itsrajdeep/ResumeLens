"""
SyncState model — Tracks incremental sync state per subreddit.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class SyncState(Base):
    __tablename__ = "sync_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subreddit = Column(String(50), nullable=False, unique=True)
    last_post_id = Column(String(20))  # Reddit post fullname (e.g., "t3_abc123")
    last_sync_at = Column(DateTime)
    total_posts_synced = Column(Integer, default=0)

    def __repr__(self):
        return f"<SyncState(subreddit={self.subreddit}, last_sync={self.last_sync_at})>"
