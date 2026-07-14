"""
Post filter — decide if a raw post dict is a resume worth processing.

Rules (all must pass):
1. Has either:
   a) A downloadable file URL (PDF or image) in media_urls, post URL, or selftext, OR
   b) A resume-related title (resume subreddits nearly always contain image posts
      even when SocialCrawl doesn't return media_urls)
2. Not removed/deleted by Reddit.
3. Score >= 0.

Works with both the old Reddit JSON shape and the SocialCrawl API shape.
"""
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.crawler.reddit_client import RESUME_FILE_EXTENSIONS

_ALLOWED_HOSTS = frozenset([
    "i.redd.it", "i.imgur.com", "imgur.com",
    "preview.redd.it", "external-preview.redd.it",
])

# Subreddits where almost every post is a resume image even without media_urls
_RESUME_SUBREDDITS = frozenset([
    "engineeringresumes", "resumes", "developersindia",
    "cscareerquestions",
])

# Title keywords that strongly indicate a resume post
_RESUME_TITLE_RE = re.compile(
    r"\b(resume|cv|feedback|rate my|review my|roast my|critique my|revamp)\b",
    re.IGNORECASE,
)

_FILE_URL_RE = re.compile(
    r"https?://\S+\.(?:pdf|png|jpg|jpeg)",
    re.IGNORECASE,
)


def _is_file_url(url: str) -> bool:
    """Return True if the URL points to a resume-compatible file."""
    if not url:
        return False
    parsed = urlparse(url)
    ext = parsed.path.rsplit(".", 1)[-1].lower().split("?")[0]
    if f".{ext}" in RESUME_FILE_EXTENSIONS:
        return True
    if parsed.netloc in _ALLOWED_HOSTS:
        return True
    return False


def _extract_file_url(post: dict) -> str | None:
    """
    Find a direct resume file URL in the post.

    Priority:
    1. _media_urls (SocialCrawl — direct image/file attachments)
    2. post url field (if it's a file/known host)
    3. selftext regex scan
    """
    # 1. SocialCrawl media_urls — most reliable
    for mu in post.get("_media_urls") or []:
        if mu and _is_file_url(str(mu)):
            return str(mu)

    # 2. Direct URL field
    url = post.get("url", "")
    if url and _is_file_url(url):
        return url

    # 3. Scan selftext for embedded URLs
    selftext = post.get("selftext", "") or ""
    match = _FILE_URL_RE.search(selftext)
    return match.group(0) if match else None


def _file_type(url: str) -> str | None:
    ext = url.rsplit(".", 1)[-1].lower().split("?")[0]
    return ext if f".{ext}" in RESUME_FILE_EXTENSIONS else None


def is_resume_post(post: dict) -> bool:
    if post.get("removed_by_category"):
        return False
    if post.get("flags", {}).get("deleted"):
        return False
    if post.get("score", 0) < 0:
        return False

    # Accept if we can find a direct file URL
    if _extract_file_url(post) is not None:
        return True

    # Accept if it's a resume-focused subreddit AND title sounds like a resume post
    # (SocialCrawl often doesn't return media_urls; pipeline will fetch the image via permalink)
    subreddit = str(post.get("subreddit") or "").lower()
    title = str(post.get("title") or "")
    if subreddit in _RESUME_SUBREDDITS and _RESUME_TITLE_RE.search(title):
        return True

    return False


def extract_post_data(post: dict) -> dict:
    """Return a DB-ready dict from a post dict (Reddit JSON or SocialCrawl shape)."""
    file_url = _extract_file_url(post)
    author = post.get("author")

    # Permalink: SocialCrawl returns full URL; old Reddit JSON returns /r/... path
    permalink = post.get("permalink") or post.get("url") or ""
    if permalink and not permalink.startswith("http"):
        permalink = f"https://reddit.com{permalink}"

    # For SocialCrawl posts without direct media URLs, use permalink as file_url
    # so the pipeline can visit the thread to extract the image
    if not file_url and permalink:
        # We'll store the Reddit thread URL; pipeline handles fetching
        file_url = None  # Keep None — pipeline skips download, post is saved for reference

    return {
        "reddit_id": post["id"],
        "subreddit": post["subreddit"],
        "title": post["title"],
        "author": author if author not in (None, "[deleted]") else None,
        "score": post.get("score", 0),
        "created_at": datetime.fromtimestamp(
            post.get("created_utc") or 0, tz=timezone.utc
        ).replace(tzinfo=None),
        "permalink": permalink,
        "file_url": file_url,
        "file_type": _file_type(file_url) if file_url else None,
    }
