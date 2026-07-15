"""
Resume endpoints — list, get, filter.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.api.deps import get_db
from app.models.resume import Resume
from app.models.post import Post
from app.models.skill import Skill, ResumeSkill
from app.schemas.resume import ResumeResponse, ResumeDetail, SkillOut

router = APIRouter()


def _attach_post(resume: Resume) -> dict:
    """Merge resume + post fields into a flat dict for ResumeResponse."""
    post: Post | None = resume.post
    return {
        "id": resume.id,
        "post_id": resume.post_id,
        "category": resume.category,
        "summary": resume.summary,
        "anonymous_file_path": resume.anonymous_file_path,
        "embedding_id": resume.embedding_id,
        "created_at": resume.created_at,
        "updated_at": resume.updated_at,
        # Post fields
        "title": post.title if post else None,
        "file_url": post.file_url if post else None,
        "file_type": post.file_type if post else None,
        "subreddit": post.subreddit if post else None,
        "score": post.score if post else None,
        "permalink": post.permalink if post else None,
        "author": post.author if post else None,
    }


@router.get("/", response_model=list[ResumeResponse])
def list_resumes(
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Resume).options(joinedload(Resume.post))
    if category:
        q = q.filter(Resume.category == category)
    offset = (page - 1) * page_size
    resumes = q.order_by(Resume.created_at.desc()).offset(offset).limit(page_size).all()
    return [_attach_post(r) for r in resumes]


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


@router.get("/count")
def resume_count(db: Session = Depends(get_db)):
    """Return total number of resumes in the database."""
    return {"count": db.query(func.count(Resume.id)).scalar()}


@router.get("/{resume_id}", response_model=ResumeDetail)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = (
        db.query(Resume)
        .options(
            joinedload(Resume.post),
            joinedload(Resume.skills).joinedload(ResumeSkill.skill),
            joinedload(Resume.projects),
        )
        .filter(Resume.id == resume_id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Flatten skills from junction table
    skills = [
        SkillOut(name=rs.skill.name, category=rs.skill.category)
        for rs in resume.skills
        if rs.skill
    ]

    result = _attach_post(resume)
    result["ocr_text"] = resume.ocr_text
    result["parsed_data"] = resume.parsed_data
    result["skills"] = skills
    result["projects"] = resume.projects
    return result
