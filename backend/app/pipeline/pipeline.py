"""
Processing Pipeline — Orchestrator
Ties together all processing phases for a single resume:

  Phase 5: Text extraction (PDF → text or OCR)
  Phase 6: AI parsing (Gemini → structured data)
  Phase 7: PII removal (Gemini → anonymized text + data)
  Phase 8: Metadata extraction (skills, projects → DB)
  Phase 9: Embedding generation + Qdrant upsert

Entry points:
  - process_resume(db, resume_id)   ← processes one resume by ID
  - process_pending(db, limit)      ← batch-processes unprocessed resumes
"""
import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.post import Post
from app.pipeline.text_extractor import extract_text_from_file
from app.pipeline.parser import parse_resume
from app.pipeline.pii_remover import remove_pii_from_text, anonymize_parsed_data
from app.pipeline.metadata import extract_and_save_metadata
from app.pipeline.embedder import generate_embedding
from app import vector_store

logger = logging.getLogger(__name__)


def process_resume(db: Session, resume_id: int) -> bool:
    """
    Run the full processing pipeline for a single resume.

    Args:
        db: Database session.
        resume_id: ID of the Resume row.

    Returns:
        True on success, False on failure.
    """
    resume = db.get(Resume, resume_id)
    if not resume:
        logger.error("Resume %d not found", resume_id)
        return False

    post = db.get(Post, resume.post_id)
    file_type = post.file_type if post else _guess_file_type(resume.raw_file_path)

    logger.info("Processing resume %d (%s)", resume_id, Path(resume.raw_file_path).name)

    # ── Phase 5: Extract text ──────────────────────────────────────────────
    try:
        ocr_text = extract_text_from_file(resume.raw_file_path, file_type or "pdf")
    except Exception as exc:
        logger.error("Text extraction failed for resume %d: %s", resume_id, exc)
        ocr_text = ""

    if not ocr_text or len(ocr_text.strip()) < 50:
        logger.warning("Resume %d: insufficient text extracted, skipping AI steps", resume_id)
        resume.ocr_text = ocr_text
        _mark_processed(db, post)
        db.commit()
        return False

    # ── Phase 6: AI Parse ─────────────────────────────────────────────────
    parsed_data = parse_resume(ocr_text)

    # ── Phase 7: PII Removal ──────────────────────────────────────────────
    clean_text = remove_pii_from_text(ocr_text)
    clean_parsed = anonymize_parsed_data(parsed_data) if parsed_data else None

    # ── Save anonymized text file ─────────────────────────────────────────
    anon_path = _save_anonymous_text(resume.raw_file_path, clean_text)

    # ── Update Resume row ─────────────────────────────────────────────────
    resume.ocr_text = clean_text
    resume.parsed_data = clean_parsed
    resume.anonymous_file_path = anon_path
    resume.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    if parsed_data:
        resume.category = parsed_data.get("category") or "Other"
        resume.summary = (clean_parsed or {}).get("summary") or ""

    db.flush()

    # ── Phase 8: Skills & Projects ────────────────────────────────────────
    if clean_parsed:
        try:
            extract_and_save_metadata(db, resume_id, clean_parsed)
        except Exception as exc:
            logger.error("Metadata extraction failed for resume %d: %s", resume_id, exc)

    # ── Phase 9: Embeddings ───────────────────────────────────────────────
    embed_text = resume.summary or clean_text
    vector = generate_embedding(embed_text)
    if vector:
        try:
            vector_store.ensure_collection()
            point_id = vector_store.upsert_resume(
                resume_id=resume_id,
                vector=vector,
                payload={
                    "resume_id": resume_id,
                    "category": resume.category,
                    "summary": resume.summary or "",
                },
            )
            resume.embedding_id = point_id
        except Exception as exc:
            logger.error("Qdrant upsert failed for resume %d: %s", resume_id, exc)

    # ── Mark post as processed ────────────────────────────────────────────
    _mark_processed(db, post)
    db.commit()

    logger.info(
        "Resume %d processed: category=%s, skills=%s, embed=%s",
        resume_id,
        resume.category,
        "yes" if clean_parsed else "no",
        "yes" if vector else "no",
    )
    return True


def process_pending(db: Session, limit: int = 50) -> dict:
    """
    Batch-process all unprocessed resumes (where ocr_text is NULL).

    Args:
        db: Database session.
        limit: Max resumes to process in one call.

    Returns:
        Summary dict: {processed, failed, skipped}.
    """
    pending = (
        db.query(Resume)
        .filter(Resume.ocr_text.is_(None))
        .limit(limit)
        .all()
    )

    processed = failed = 0
    for resume in pending:
        try:
            success = process_resume(db, resume.id)
            if success:
                processed += 1
            else:
                failed += 1
        except Exception as exc:
            logger.error("Pipeline error for resume %d: %s", resume.id, exc)
            db.rollback()
            failed += 1

    summary = {"processed": processed, "failed": failed, "total": len(pending)}
    logger.info("Batch pipeline complete: %s", summary)
    return summary


def _save_anonymous_text(raw_file_path: str, clean_text: str) -> str | None:
    """Save anonymized text to the anonymous storage directory."""
    try:
        from app.config import get_settings
        settings = get_settings()

        raw_path = Path(raw_file_path)
        anon_dir = Path(settings.anonymous_storage_path) / raw_path.parent.name
        anon_dir.mkdir(parents=True, exist_ok=True)

        anon_path = anon_dir / f"{raw_path.stem}.txt"
        anon_path.write_text(clean_text, encoding="utf-8")
        return str(anon_path)
    except Exception as exc:
        logger.error("Failed to save anonymous text: %s", exc)
        return None


def _mark_processed(db: Session, post: Post | None) -> None:
    """Mark the parent post as processed."""
    if post:
        post.processed = True
        db.flush()


def _guess_file_type(file_path: str) -> str:
    """Guess file type from extension."""
    suffix = Path(file_path).suffix.lower().lstrip(".")
    return suffix if suffix in {"pdf", "png", "jpg", "jpeg"} else "pdf"
