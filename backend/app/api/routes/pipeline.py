"""
Pipeline API Routes
Trigger and monitor the AI processing pipeline.

POST /api/pipeline/trigger        ← Process all pending resumes in background
POST /api/pipeline/trigger/{id}   ← Process a specific resume
GET  /api/pipeline/status         ← Count of processed vs unprocessed resumes
"""
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db
from app.models.resume import Resume

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/trigger")
def trigger_pipeline(
    background_tasks: BackgroundTasks,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Process pending (unprocessed) resumes in the background.
    Resumes without ocr_text are considered unprocessed.
    """
    pending_count = db.query(func.count(Resume.id)).filter(Resume.ocr_text.is_(None)).scalar()

    if pending_count == 0:
        return {"status": "no_pending", "message": "All resumes are already processed."}

    background_tasks.add_task(_run_pipeline_batch, limit)
    return {
        "status": "started",
        "message": f"Processing up to {limit} of {pending_count} pending resumes in background.",
        "pending": pending_count,
    }


@router.post("/trigger/{resume_id}")
def trigger_single(
    resume_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Process a specific resume by ID."""
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    background_tasks.add_task(_run_single, resume_id)
    return {"status": "started", "resume_id": resume_id}


@router.get("/status")
def pipeline_status(db: Session = Depends(get_db)):
    """Return pipeline processing statistics."""
    total = db.query(func.count(Resume.id)).scalar() or 0
    processed = db.query(func.count(Resume.id)).filter(Resume.ocr_text.isnot(None)).scalar() or 0
    pending = total - processed

    categorized = (
        db.query(Resume.category, func.count(Resume.id).label("count"))
        .filter(Resume.category.isnot(None))
        .group_by(Resume.category)
        .all()
    )

    return {
        "total_resumes": total,
        "processed": processed,
        "pending": pending,
        "by_category": [{"category": r.category, "count": r.count} for r in categorized],
    }


def _run_pipeline_batch(limit: int):
    """Background task: run full pipeline on pending resumes."""
    from app.database import SessionLocal
    from app.pipeline.pipeline import process_pending

    db = SessionLocal()
    try:
        summary = process_pending(db, limit=limit)
        logger.info("Pipeline batch done: %s", summary)
    except Exception as exc:
        logger.error("Pipeline batch error: %s", exc)
    finally:
        db.close()


def _run_single(resume_id: int):
    """Background task: process a single resume."""
    from app.database import SessionLocal
    from app.pipeline.pipeline import process_resume

    db = SessionLocal()
    try:
        process_resume(db, resume_id)
    except Exception as exc:
        logger.error("Pipeline error for resume %d: %s", resume_id, exc)
    finally:
        db.close()
