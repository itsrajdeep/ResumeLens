"""
Crawl endpoints — trigger and monitor Reddit sync.
"""
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.config import get_settings
from app.crawler.sync import sync_subreddit
from app.models.sync_state import SyncState

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.post("/trigger")
def trigger_crawl(
    background_tasks: BackgroundTasks,
    subreddits: list[str] | None = None,
    db: Session = Depends(get_db),
):
    """
    Trigger an incremental crawl in the background.
    Defaults to the subreddits configured in settings.
    """
    targets = subreddits or settings.target_subreddits
    if not targets:
        raise HTTPException(status_code=400, detail="No subreddits specified.")

    for sub in targets:
        background_tasks.add_task(_run_sync, sub)

    return {"status": "crawl started", "subreddits": targets}


def _run_sync(subreddit: str):
    """Background task wrapper — gets its own DB session."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        sync_subreddit(db, subreddit)
    except Exception as exc:
        logger.error("Sync failed for r/%s: %s", subreddit, exc)
    finally:
        db.close()


@router.get("/status")
def crawl_status(db: Session = Depends(get_db)):
    """Return the last sync state for each tracked subreddit."""
    states = db.query(SyncState).all()
    return [
        {
            "subreddit": s.subreddit,
            "last_post_id": s.last_post_id,
            "last_sync_at": s.last_sync_at,
            "total_posts_synced": s.total_posts_synced,
        }
        for s in states
    ]
