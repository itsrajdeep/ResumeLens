"""
Post filter — decide if a raw Reddit JSON post dict is a resume worth processing.

Rules (all must pass):
1. Has a downloadable file URL (PDF or image) in post URL or selftext.
2. Not removed by Reddit.
3. Score >= 0.
"""
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.crawler.reddit_client import RESUME_FILE_EXTENSIONS

_ALLOWED_HOSTS = frozenset([
    "i.redd.it", "i.imgur.com", "imgur.com",
    "preview.redd.it", "external-preview.redd.it",
])

_FILE_URL_RE = re.compile(
    r"https?://\S+\.(?:pdf|png|jpg|jpeg)",
    re.IGNORECASE,
)


def _extract_file_url(post: dict) -> str | None:
    url = post.get("url", "")
    parsed = urlparse(url)
    ext = parsed.path.rsplit(".", 1)[-1].lower()

    if f".{ext}" in RESUME_FILE_EXTENSIONS:
        return url
    if parsed.netloc in _ALLOWED_HOSTS:
        return url

    selftext = post.get("selftext", "") or ""
    match = _FILE_URL_RE.search(selftext)
    return match.group(0) if match else None


def _file_type(url: str) -> str | None:
    ext = url.rsplit(".", 1)[-1].lower().split("?")[0]
    return ext if f".{ext}" in RESUME_FILE_EXTENSIONS else None


def is_resume_post(post: dict) -> bool:
    if post.get("removed_by_category"):
        return False
    if post.get("score", 0) < 0:
        return False
    return _extract_file_url(post) is not None


def extract_post_data(post: dict) -> dict:
    """Return a DB-ready dict from a raw Reddit JSON post dict."""
    file_url = _extract_file_url(post)
    author = post.get("author")
    return {
        "reddit_id": post["id"],
        "subreddit": post["subreddit"],
        "title": post["title"],
        "author": author if author not in (None, "[deleted]") else None,
        "score": post.get("score", 0),
        "created_at": datetime.fromtimestamp(post["created_utc"], tz=timezone.utc).replace(tzinfo=None),
        "permalink": f"https://reddit.com{post['permalink']}",
        "file_url": file_url,
        "file_type": _file_type(file_url) if file_url else None,
    }
