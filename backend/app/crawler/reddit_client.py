"""
Reddit client — uses SocialCrawl API (https://www.socialcrawl.dev)
to fetch subreddit posts without needing Reddit OAuth credentials.

SocialCrawl response shape (confirmed from API):
{
  "success": true,
  "data": {
    "items": [
      {
        "post": {
          "id": "pt1z6p",
          "url": "https://reddit.com/r/.../comments/...",   ← Reddit thread URL
          "content": {
            "text": "<post title>",
            "media_urls": ["https://i.redd.it/..."],        ← actual image/file URL
            "thumbnail_url": "..."
          },
          "author": {"username": "...", "display_name": "..."},
          "engagement": {"likes": 5, "comments": 3, ...},
          "flags": {"deleted": false, "nsfw": false},
          "published_at": "2021-09-22T06:58:06.000Z",
          "ext": {"subreddit": "EngineeringResumes", "published_at_epoch": 1632293886}
        }
      }
    ]
  },
  "pagination": {"next_cursor": null, "has_more": false}
}
"""
import logging
import time
from typing import Iterator

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_BASE_URL = "https://www.socialcrawl.dev/v1/reddit/subreddit/search"
_RATE_SLEEP = 1.0  # seconds between paginated requests

# File extensions we consider downloadable resume files
RESUME_FILE_EXTENSIONS = frozenset([".pdf", ".png", ".jpg", ".jpeg"])


def _extract_file_url(post: dict) -> str | None:
    """
    Extract a direct file URL from the SocialCrawl post object.
    Priority: media_urls[] → thumbnail_url → None
    """
    content = post.get("content") or {}

    # media_urls is the primary field for image/file attachments
    media_urls = content.get("media_urls") or []
    if media_urls:
        for mu in media_urls:
            if mu:
                return str(mu)

    # Thumbnail as fallback
    thumb = content.get("thumbnail_url")
    if thumb:
        return str(thumb)

    return None


def _parse_post(post_obj: dict, subreddit: str) -> dict:
    """
    Map a SocialCrawl 'post' sub-object to the flat dict that
    post_filter.py and sync.py expect (mirrors old Reddit JSON shape).
    """
    ext = post_obj.get("ext") or {}
    content = post_obj.get("content") or {}
    author = post_obj.get("author") or {}
    engagement = post_obj.get("engagement") or {}
    flags = post_obj.get("flags") or {}

    # ID — plain string like "pt1z6p"
    post_id = str(post_obj.get("id") or "")

    # Title lives in content.text for SocialCrawl
    title = content.get("text") or post_obj.get("title") or ""

    # Score
    score = int(engagement.get("likes") or engagement.get("score") or 0)

    # Timestamp — prefer epoch from ext, fallback to parsing published_at
    epoch = ext.get("published_at_epoch")
    if not epoch:
        ts_str = post_obj.get("published_at") or ""
        if ts_str:
            try:
                from datetime import datetime, timezone
                epoch = datetime.fromisoformat(
                    ts_str.replace("Z", "+00:00")
                ).timestamp()
            except ValueError:
                epoch = 0.0
        else:
            epoch = 0.0

    # Permalink — SocialCrawl returns the full Reddit URL as url
    permalink = post_obj.get("url") or ""

    # File URL — from media attachments
    file_url = _extract_file_url(post_obj)

    # Deleted/removed flag
    removed = None
    if flags.get("deleted"):
        removed = "deleted"

    return {
        "id": post_id,
        "subreddit": ext.get("subreddit") or subreddit,
        "title": title,
        "author": author.get("username") or "[deleted]",
        "score": score,
        "created_utc": float(epoch),
        "permalink": permalink,
        # url = file URL if present, else the Reddit thread URL (for selftext posts)
        "url": file_url or permalink,
        "selftext": "",          # SocialCrawl doesn't return post body text
        "removed_by_category": removed,
        # Pass through the raw media_urls so post_filter can check them
        "_media_urls": content.get("media_urls") or [],
    }


def iter_subreddit_posts(
    subreddit: str,
    limit: int = 100,
    after: str | None = None,
) -> Iterator[dict]:
    """
    Yield normalized post dicts from r/{subreddit} via SocialCrawl API.

    Automatically paginates via next_cursor until `limit` posts yielded
    or no more pages remain.

    Args:
        subreddit: Subreddit name (no r/ prefix).
        limit: Total posts to yield.
        after: Kept for API compatibility; SocialCrawl uses cursor pagination.
    """
    api_key = settings.socialcrawl_api_key
    if not api_key:
        logger.error(
            "SOCIALCRAWL_API_KEY is not set in .env. "
            "Get a free API key at https://www.socialcrawl.dev"
        )
        return

    headers = {"x-api-key": api_key}
    fetched = 0
    cursor: str | None = None
    first_page = True

    with httpx.Client(timeout=20, follow_redirects=True) as client:
        while fetched < limit:
            params: dict = {
                "subreddit": subreddit,
                "sort": "new",
                "limit": min(25, limit - fetched),
            }
            if cursor:
                params["cursor"] = cursor

            try:
                resp = client.get(_BASE_URL, params=params, headers=headers)
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "SocialCrawl API error for r/%s [%s]: %s",
                    subreddit, exc.response.status_code, exc.response.text[:300],
                )
                break
            except httpx.HTTPError as exc:
                logger.error("SocialCrawl network error for r/%s: %s", subreddit, exc)
                break

            body = resp.json()
            if not body.get("success"):
                logger.error("SocialCrawl returned non-success for r/%s: %s", subreddit, body)
                break

            data = body.get("data") or {}
            raw_items = data.get("items") or []

            if not raw_items:
                logger.info("No items returned from SocialCrawl for r/%s", subreddit)
                break

            if first_page:
                logger.info(
                    "SocialCrawl: %d credits remaining, cached=%s",
                    body.get("credits_remaining", "?"),
                    body.get("cached", "?"),
                )
                first_page = False

            for item in raw_items:
                if fetched >= limit:
                    return
                # Each item has a "post" sub-object
                post_obj = item.get("post") or item
                yield _parse_post(post_obj, subreddit)
                fetched += 1

            # Pagination
            pagination = body.get("pagination") or {}
            cursor = pagination.get("next_cursor")
            has_more = pagination.get("has_more", False)

            if not cursor or not has_more:
                logger.info(
                    "SocialCrawl: no more pages for r/%s (fetched %d)", subreddit, fetched
                )
                break

            time.sleep(_RATE_SLEEP)
