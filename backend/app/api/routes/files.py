"""
File Serving Routes
Serves anonymized resume files and anonymous text.

GET /api/files/{resume_id}/text     ← Returns anonymized text content
GET /api/files/{resume_id}/download ← Redirects to Supabase CDN (prod) or streams from disk (local)
"""
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.resume import Resume

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{resume_id}/text", response_class=PlainTextResponse)
def get_resume_text(resume_id: int, db: Session = Depends(get_db)):
    """
    Return the anonymized plain-text content of a resume.
    This is the PII-stripped version safe to display in the UI.
    """
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if resume.ocr_text:
        return resume.ocr_text

    # Fallback: read from anonymous file if DB text is missing
    if resume.anonymous_file_path:
        anon_path = Path(resume.anonymous_file_path)
        if anon_path.exists() and anon_path.suffix == ".txt":
            return anon_path.read_text(encoding="utf-8")

    raise HTTPException(
        status_code=404,
        detail="Resume text not yet processed. Try again after the pipeline runs.",
    )


@router.get("/{resume_id}/download")
def download_resume_file(resume_id: int, db: Session = Depends(get_db)):
    """
    Serve the resume file.
    - Production: redirect to permanent Supabase Storage public URL.
    - Local dev:  stream the anonymized .txt file from disk.
    """
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # ── Production: redirect to Supabase CDN (permanent, survives restarts) ──
    if resume.supabase_url:
        return RedirectResponse(url=resume.supabase_url, status_code=302)

    # ── Local dev fallback: serve anonymized text from disk ───────────────────
    if not resume.anonymous_file_path:
        raise HTTPException(
            status_code=404,
            detail="Anonymized file not yet available. Pipeline has not processed this resume.",
        )

    anon_path = Path(resume.anonymous_file_path)
    if not anon_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=str(anon_path),
        media_type="text/plain",
        filename=f"resume_{resume_id}_anonymized.txt",
    )
