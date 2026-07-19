"""
Supabase Storage — Upload resume files and get permanent public URLs.

Files are uploaded to the 'resumes' public bucket.
This replaces ephemeral local disk storage for production deployments.
"""
import logging
import mimetypes
from pathlib import Path

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    """Lazy-initialise the Supabase client (only when actually needed)."""
    global _client
    if _client is None:
        from supabase import create_client
        from app.config import get_settings
        s = get_settings()
        if not s.supabase_url or not s.supabase_service_key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set for cloud storage."
            )
        _client = create_client(s.supabase_url, s.supabase_service_key)
    return _client


def upload_file(local_path: str, storage_key: str) -> str:
    """
    Upload a local file to Supabase Storage and return its permanent public URL.

    Args:
        local_path:  Absolute path to the file on disk.
        storage_key: Destination path inside the bucket, e.g. 'EngineeringResumes/abc123.pdf'

    Returns:
        Public URL string, e.g. https://xxx.supabase.co/storage/v1/object/public/resumes/...
    """
    from app.config import get_settings
    s = get_settings()

    path = Path(local_path)
    content_type, _ = mimetypes.guess_type(str(path))
    content_type = content_type or "application/octet-stream"

    client = _get_client()
    with open(local_path, "rb") as f:
        client.storage.from_(s.supabase_bucket).upload(
            path=storage_key,
            file=f,
            file_options={"content-type": content_type, "upsert": "true"},
        )

    public_url = (
        f"{s.supabase_url}/storage/v1/object/public/{s.supabase_bucket}/{storage_key}"
    )
    logger.info("Uploaded %s → %s", local_path, public_url)
    return public_url


def is_configured() -> bool:
    """Return True if Supabase credentials are set (prod). False = local mode."""
    from app.config import get_settings
    s = get_settings()
    return bool(s.supabase_url and s.supabase_service_key)
