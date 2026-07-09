"""
Reddit client — uses Reddit's public JSON endpoints. No API key needed.

URL pattern: https://www.reddit.com/r/{subreddit}/new.json?limit=100&after=t3_xxx
Rate limit: ~1 req/2s for unauthenticated. We sleep between pages.
"""
import logging
import time
from typing import Iterator

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_BASE = "https://www.reddit.com"
_HEADERS = {"User-Agent": settings.reddit_user_agent}
_PAGE_LIMIT = 100   # Reddit max per request
_RATE_SLEEP = 2.0   # seconds between requests (stay under 30/min limit)

# File extensions we consider downloadable resume files
RESUME_FILE_EXTENSIONS = frozenset([".pdf", ".png", ".jpg", ".jpeg"])


def iter_subreddit_posts(
    subreddit: str,
    limit: int = 100,
    after: str | None = None,
) -> Iterator[dict]:
    """
    Yield raw post dicts from r/{subreddit}/new.json.

    Automatically paginates until `limit` posts are yielded or Reddit
    returns no more results. Each dict is Reddit's raw "data" child object.

    Args:
        subreddit: Subreddit name (no r/ prefix).
        limit: Total posts to yield (across pages).
        after: Fullname to paginate from (e.g. "t3_abc123").
    """
    fetched = 0
    params: dict = {"limit": min(_PAGE_LIMIT, limit), "raw_json": 1}
    if after:
        params["after"] = after

    url = f"{_BASE}/r/{subreddit}/new.json"

    with httpx.Client(headers=_HEADERS, follow_redirects=True, timeout=15) as client:
        while fetched < limit:
            try:
                resp = client.get(url, params=params)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                logger.error("Reddit JSON fetch failed for r/%s: %s", subreddit, exc)
                break

            data = resp.json().get("data", {})
            children = data.get("children", [])
            if not children:
                break

            for child in children:
                if fetched >= limit:
                    return
                yield child["data"]
                fetched += 1

            after = data.get("after")
            if not after:
                break

            params["after"] = after
            time.sleep(_RATE_SLEEP)
