"""
Incremental sync — crawl subreddits via Reddit JSON and persist new resume posts.

Sync strategy:
  - Per subreddit, record the newest post's fullname (t3_<id>) in sync_state.
  - On next run, fetch from newest; stop when we hit last_post_id.
  - Dedup via reddit_id unique constraint.
"""
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.crawler.downloader import download_resume
from app.crawler.post_filter import extract_post_data, is_resume_post
from app.crawler.reddit_client import iter_subreddit_posts
from app.models.post import Post
from app.models.resume import Resume
from app.models.sync_state import SyncState

logger = logging.getLogger(__name__)


def _get_or_create_sync_state(db: Session, subreddit: str) -> SyncState:
    state = db.query(SyncState).filter(SyncState.subreddit == subreddit).first()
    if not state:
        state = SyncState(subreddit=subreddit, total_posts_synced=0)
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


def sync_subreddit(db: Session, subreddit: str, limit: int = 100) -> dict:
    """
    Crawl `subreddit`, saving new resume posts and downloading files.
    Returns a summary dict: {subreddit, new_posts, skipped, errors}.
    """
    state = _get_or_create_sync_state(db, subreddit)
    state_id = state.id  # Cache the ID — survive rollbacks
    last_post_id = state.last_post_id  # Cache — survive rollbacks

    new_posts = skipped = errors = 0
    newest_fullname: str | None = None
    _pending_resume_ids: list[int] = []

    for post in iter_subreddit_posts(subreddit, limit=limit):
        fullname = f"t3_{post['id']}"

        if newest_fullname is None:
            newest_fullname = fullname

        if last_post_id and fullname == last_post_id:
            logger.info("Reached last sync point (%s), stopping.", fullname)
            break

        if not is_resume_post(post):
            skipped += 1
            continue

        if db.query(Post).filter(Post.reddit_id == post["id"]).first():
            skipped += 1
            continue

        try:
            data = extract_post_data(post)
            db_post = Post(**data)
            db.add(db_post)
            db.flush()

            if data["file_url"] and data["file_type"]:
                try:
                    file_path, file_hash, is_new = download_resume(
                        data["file_url"], subreddit, data["file_type"], db
                    )
                    if is_new:
                        new_resume = Resume(
                            post_id=db_post.id,
                            raw_file_path=file_path,
                            file_hash=file_hash,
                        )
                        db.add(new_resume)
                        db.flush()
                        # Trigger pipeline in background after commit
                        _pending_resume_ids.append(new_resume.id)
                except Exception as dl_err:
                    logger.warning("Download failed for %s: %s", data["file_url"], dl_err)

            db.commit()
            new_posts += 1

        except Exception as exc:
            logger.error("Error processing %s: %s", post.get("id"), exc)
            db.rollback()
            errors += 1
            continue

    # Update sync state — re-query by ID to avoid detached-instance issues after rollback
    try:
        state = db.query(SyncState).filter(SyncState.id == state_id).first()
        if state:
            if newest_fullname:
                state.last_post_id = newest_fullname
            state.last_sync_at = datetime.now(timezone.utc).replace(tzinfo=None)
            state.total_posts_synced = (state.total_posts_synced or 0) + new_posts
            db.commit()
    except Exception as exc:
        logger.error("Failed to update sync state for r/%s: %s", subreddit, exc)
        db.rollback()

    summary = {
        "subreddit": subreddit,
        "new_posts": new_posts,
        "skipped": skipped,
        "errors": errors,
        "pending_pipeline": _pending_resume_ids,
    }
    logger.info("Sync complete: %s", summary)
    return summary
