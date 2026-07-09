"""
Resume endpoints — list, get, filter.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from app.api.deps import get_db
from app.models.resume import Resume
from app.models.skill import Skill, ResumeSkill
from app.schemas.resume import ResumeResponse, ResumeDetail

router = APIRouter()


@router.get("/", response_model=list[ResumeResponse])
def list_resumes(
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Resume)
    if category:
        q = q.filter(Resume.category == category)
    offset = (page - 1) * page_size
    return q.order_by(Resume.created_at.desc()).offset(offset).limit(page_size).all()


@router.get("/{resume_id}", response_model=ResumeDetail)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.get("/stats/categories")
def category_stats(db: Session = Depends(get_db)):
    """Return count of resumes per category."""
    rows = (
        db.query(Resume.category, func.count(Resume.id).label("count"))
        .group_by(Resume.category)
        .all()
    )
    return [{"category": r.category or "uncategorized", "count": r.count} for r in rows]


@router.get("/stats/skills")
def top_skills(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """Return top N skills by usage count."""
    rows = db.query(Skill).order_by(Skill.usage_count.desc()).limit(limit).all()
    return [{"name": s.name, "category": s.category, "count": s.usage_count} for s in rows]
