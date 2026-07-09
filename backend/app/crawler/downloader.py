"""
Downloader — fetches resume files from URLs, deduplicates by SHA256 hash.

Flow:
  1. HEAD request to check Content-Type / size before downloading.
  2. Stream download to a temp file.
  3. SHA256 the content; if hash exists in DB, skip storage.
  4. Move file to storage/raw/<subreddit>/<hash>.<ext>.
"""
import hashlib
import logging
import shutil
import tempfile
from pathlib import Path

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.resume import Resume

logger = logging.getLogger(__name__)
settings = get_settings()

# 20 MB max resume file size
_MAX_FILE_BYTES = 20 * 1024 * 1024

_HEADERS = {
    "User-Agent": settings.reddit_user_agent,
}


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def download_resume(
    url: str,
    subreddit: str,
    file_type: str,
    db: Session,
) -> tuple[str, bool]:
    """
    Download a resume file and persist it to disk.

    Returns:
        (file_path, is_new): absolute path on disk, and whether this was a new file.

    Raises:
        ValueError: if the file is too large or content-type is unexpected.
        httpx.HTTPError: on network failure.
    """
    raw_root = Path(settings.raw_storage_path) / subreddit
    raw_root.mkdir(parents=True, exist_ok=True)

    with httpx.Client(follow_redirects=True, timeout=30) as client:
        # Stream download to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp:
            tmp_path = Path(tmp.name)
            bytes_written = 0

            with client.stream("GET", url, headers=_HEADERS) as response:
                response.raise_for_status()
                for chunk in response.iter_bytes(chunk_size=65536):
                    bytes_written += len(chunk)
                    if bytes_written > _MAX_FILE_BYTES:
                        tmp_path.unlink(missing_ok=True)
                        raise ValueError(f"File exceeds {_MAX_FILE_BYTES // 1024 // 1024}MB limit: {url}")
                    tmp.write(chunk)

    file_hash = _sha256_of_file(tmp_path)

    # Dedup: if hash already in DB, discard temp file
    existing = db.query(Resume).filter(Resume.file_hash == file_hash).first()
    if existing:
        tmp_path.unlink(missing_ok=True)
        logger.debug("Duplicate file skipped (hash=%s)", file_hash[:12])
        return existing.raw_file_path, False

    dest = raw_root / f"{file_hash}.{file_type}"
    shutil.move(str(tmp_path), dest)
    logger.info("Downloaded %s → %s", url, dest)
    return str(dest), True
