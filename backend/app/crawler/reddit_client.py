"""
Reddit client — uses Playwright to scrape subreddit posts by intercepting
Reddit's internal network requests (no API key required).

Strategy:
  1. Launch a headless Chromium browser via Playwright.
  2. Navigate to the subreddit's new page.
  3. Intercept XHR/fetch requests matching Reddit's internal "svc/shreddit/graphql"
     or "gateway.reddit.com" endpoints to capture raw post JSON.
  4. Scroll the page to trigger pagination / infinite scroll.
  5. Normalize captured posts into the flat dict expected by post_filter.py and sync.py.

Normalized post dict shape:
    {
        "id":               str,       # e.g. "pt1z6p"
        "subreddit":        str,       # e.g. "EngineeringResumes"
        "title":            str,
        "author":           str,
        "score":            int,
        "created_utc":      float,     # Unix epoch
        "permalink":        str,       # Full Reddit URL
        "url":              str,       # File URL or permalink
        "selftext":         str,       # Post body text (if any)
        "removed_by_category": str | None,
        "_media_urls":      list[str], # Direct image/file URLs
    }
"""
import logging
import time
import json
from datetime import datetime, timezone
from typing import Iterator

logger = logging.getLogger(__name__)

# File extensions we consider downloadable resume files
RESUME_FILE_EXTENSIONS = frozenset([".pdf", ".png", ".jpg", ".jpeg"])

# Reddit domains to intercept network requests from
_INTERCEPT_PATTERNS = [
    "**/svc/shreddit/**",
    "**/gateway.reddit.com/**",
    "**/www.reddit.com/r/*/new.json**",
    "**reddit.com/r/*/new.json**",
    "**/oauth.reddit.com/**",
]

# How long to wait (ms) after scroll before capturing data
_SCROLL_WAIT_MS = 2500
# How many scroll iterations to do per pagination cycle
_SCROLL_ITERATIONS = 3


def _extract_media_urls_from_post(raw: dict) -> list[str]:
    """Extract all direct image/file URLs from a raw Reddit post object."""
    urls: list[str] = []

    # Reddit's new API shape: data.children[].data
    # Field: url_overridden_by_dest or url
    for field in ("url_overridden_by_dest", "url"):
        val = raw.get(field, "")
        if val and any(val.lower().endswith(ext) for ext in RESUME_FILE_EXTENSIONS):
            urls.append(val)
            break

    # Gallery posts: media_metadata dict
    mm = raw.get("media_metadata") or {}
    for meta in mm.values():
        # Each entry has 's' (source) with 'u' (url)
        src = (meta.get("s") or {}).get("u", "")
        if src:
            # Reddit encodes & as &amp; in JSON sometimes
            urls.append(src.replace("&amp;", "&"))

    # Preview images (lower priority, but still useful)
    preview = (raw.get("preview") or {}).get("images") or []
    for img in preview:
        src_url = (img.get("source") or {}).get("url", "")
        if src_url:
            urls.append(src_url.replace("&amp;", "&"))

    return list(dict.fromkeys(urls))  # deduplicate, preserve order


def _normalize_post(raw: dict, subreddit: str) -> dict:
    """Normalize a Reddit API post 'data' dict into our flat format."""
    post_id = str(raw.get("id") or "")
    title = str(raw.get("title") or "")
    author = str(raw.get("author") or "[deleted]")
    score = int(raw.get("score") or 0)
    created_utc = float(raw.get("created_utc") or 0.0)
    permalink = raw.get("permalink") or ""
    if permalink and not permalink.startswith("http"):
        permalink = f"https://www.reddit.com{permalink}"
    selftext = str(raw.get("selftext") or "")
    removed = raw.get("removed_by_category") or raw.get("banned_by")

    media_urls = _extract_media_urls_from_post(raw)

    # Primary URL — prefer a direct file URL, fallback to permalink
    primary_url = media_urls[0] if media_urls else permalink

    return {
        "id": post_id,
        "subreddit": raw.get("subreddit") or subreddit,
        "title": title,
        "author": author,
        "score": score,
        "created_utc": created_utc,
        "permalink": permalink,
        "url": primary_url,
        "selftext": selftext,
        "removed_by_category": str(removed) if removed else None,
        "_media_urls": media_urls,
    }


def _parse_reddit_listing_json(body: str, subreddit: str) -> list[dict]:
    """
    Parse a Reddit listing JSON response (the .json endpoint format)
    and return a list of normalized post dicts.
    """
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return []

    posts: list[dict] = []

    # Standard listing: {"data": {"children": [{"kind": "t3", "data": {...}}]}}
    if isinstance(data, dict):
        children = (data.get("data") or {}).get("children") or []
        for child in children:
            if child.get("kind") == "t3":
                raw = child.get("data") or {}
                if raw.get("id"):
                    posts.append(_normalize_post(raw, subreddit))

    # Array of two listings (link + comment): take first
    elif isinstance(data, list) and data:
        children = (data[0].get("data") or {}).get("children") or []
        for child in children:
            if child.get("kind") == "t3":
                raw = child.get("data") or {}
                if raw.get("id"):
                    posts.append(_normalize_post(raw, subreddit))

    return posts


def iter_subreddit_posts(
    subreddit: str,
    limit: int = 100,
    after: str | None = None,
) -> Iterator[dict]:
    """
    Yield normalized post dicts from r/{subreddit} using Playwright
    to intercept Reddit's internal network requests.

    Args:
        subreddit: Subreddit name (no r/ prefix).
        limit: Maximum number of posts to yield.
        after: Optional Reddit post fullname to start after (for pagination).
    """
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        logger.error(
            "Playwright is not installed. Run: pip install playwright && "
            "playwright install chromium"
        )
        return

    captured_posts: list[dict] = []
    seen_ids: set[str] = set()

    url = f"https://www.reddit.com/r/{subreddit}/new/"
    if after:
        url += f"?after={after}"

    logger.info("Playwright: launching browser for r/%s", subreddit)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )

        # ------------------------------------------------------------------
        # Intercept network responses to grab Reddit's JSON API calls
        # ------------------------------------------------------------------
        def handle_response(response):
            try:
                req_url = response.url
                # We only care about Reddit's listing JSON endpoints
                if (
                    f"/r/{subreddit}" in req_url
                    and ("new.json" in req_url or "sort=new" in req_url)
                    and response.status == 200
                ):
                    try:
                        body = response.text()
                        new_posts = _parse_reddit_listing_json(body, subreddit)
                        for p in new_posts:
                            if p["id"] and p["id"] not in seen_ids:
                                seen_ids.add(p["id"])
                                captured_posts.append(p)
                        if new_posts:
                            logger.debug(
                                "Intercepted %d posts from %s", len(new_posts), req_url
                            )
                    except Exception as parse_err:
                        logger.debug("Could not parse intercepted response: %s", parse_err)
            except Exception:
                pass

        page = context.new_page()
        page.on("response", handle_response)

        try:
            logger.info("Playwright: navigating to %s", url)
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)  # Let initial posts load

            # ---------------------------------------------------------------
            # Scroll to trigger Reddit's infinite scroll / load more posts
            # ---------------------------------------------------------------
            scroll_round = 0
            while len(captured_posts) < limit:
                scroll_round += 1
                prev_count = len(captured_posts)

                # Scroll to bottom
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(_SCROLL_WAIT_MS)

                # Also try clicking "Load more" buttons if they exist
                try:
                    load_more = page.query_selector("[data-testid='load-more-button']")
                    if load_more:
                        load_more.click()
                        page.wait_for_timeout(2000)
                except Exception:
                    pass

                # If no new posts after scroll, try the .json endpoint directly
                if len(captured_posts) == prev_count:
                    logger.debug(
                        "No new posts after scroll %d; trying .json endpoint", scroll_round
                    )
                    after_param = f"t3_{captured_posts[-1]['id']}" if captured_posts else ""
                    json_url = (
                        f"https://www.reddit.com/r/{subreddit}/new.json"
                        f"?sort=new&limit=25"
                        + (f"&after={after_param}" if after_param else "")
                    )
                    try:
                        api_response = page.evaluate(
                            f"""async () => {{
                                const r = await fetch('{json_url}', {{
                                    headers: {{'User-Agent': 'ResumeAtlas/1.0'}}
                                }});
                                return await r.text();
                            }}"""
                        )
                        new_posts = _parse_reddit_listing_json(api_response, subreddit)
                        added = 0
                        for p in new_posts:
                            if p["id"] and p["id"] not in seen_ids:
                                seen_ids.add(p["id"])
                                captured_posts.append(p)
                                added += 1
                        logger.debug("Fetched %d posts via .json endpoint", added)
                        if added == 0:
                            logger.info(
                                "No more posts available for r/%s after %d posts",
                                subreddit, len(captured_posts)
                            )
                            break
                    except Exception as fetch_err:
                        logger.warning("In-page fetch failed: %s", fetch_err)
                        break

                if scroll_round >= _SCROLL_ITERATIONS * 3:
                    logger.info(
                        "Playwright: reached max scroll limit for r/%s", subreddit
                    )
                    break

        except PWTimeout:
            logger.warning(
                "Playwright timed out navigating to r/%s — yielding %d posts captured so far",
                subreddit, len(captured_posts)
            )
        except Exception as exc:
            logger.error("Playwright error for r/%s: %s", subreddit, exc)
        finally:
            page.close()
            context.close()
            browser.close()

    logger.info(
        "Playwright: captured %d total posts for r/%s", len(captured_posts), subreddit
    )

    # Yield up to `limit` posts
    for post in captured_posts[:limit]:
        yield post
