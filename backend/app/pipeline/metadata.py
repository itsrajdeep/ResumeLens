"""
Metadata Extractor — Phase 8
Extracts skills and projects from parsed_data and persists them to the DB.

- Upserts skills into the `skills` table with category info
- Increments usage_count for each skill
- Creates ResumeSkill junction records
- Upserts projects into the `projects` table
"""
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.skill import Skill, ResumeSkill
from app.models.project import Project

logger = logging.getLogger(__name__)

# Maps parsed skill categories from Gemini to DB category values
_SKILL_CATEGORY_MAP = {
    "languages": "language",
    "frameworks": "framework",
    "databases": "database",
    "cloud": "cloud",
    "tools": "tool",
}


def extract_and_save_metadata(
    db: Session,
    resume_id: int,
    parsed_data: dict[str, Any],
) -> None:
    """
    Extract skills and projects from parsed_data and persist to DB.

    Args:
        db: SQLAlchemy session.
        resume_id: ID of the Resume row to attach metadata to.
        parsed_data: Structured dict from parser.py.
    """
    if not parsed_data:
        logger.warning("No parsed_data for resume %d", resume_id)
        return

    _save_skills(db, resume_id, parsed_data.get("skills", {}))
    _save_projects(db, resume_id, parsed_data.get("projects", []))


def _save_skills(
    db: Session,
    resume_id: int,
    skills_dict: dict[str, list[str]],
) -> None:
    """Upsert skills and create resume_skills links."""
    for section_key, skill_names in skills_dict.items():
        if not isinstance(skill_names, list):
            continue

        db_category = _SKILL_CATEGORY_MAP.get(section_key, "tool")

        for raw_name in skill_names:
            name = _normalize_skill_name(raw_name)
            if not name:
                continue

            # Upsert skill
            skill = db.query(Skill).filter(Skill.name == name).first()
            if skill is None:
                skill = Skill(name=name, category=db_category, usage_count=0)
                db.add(skill)
                db.flush()

            skill.usage_count = (skill.usage_count or 0) + 1

            # Create junction if not exists
            exists = (
                db.query(ResumeSkill)
                .filter(
                    ResumeSkill.resume_id == resume_id,
                    ResumeSkill.skill_id == skill.id,
                )
                .first()
            )
            if not exists:
                db.add(ResumeSkill(resume_id=resume_id, skill_id=skill.id))

    db.flush()
    logger.info("Skills saved for resume %d", resume_id)


def _save_projects(
    db: Session,
    resume_id: int,
    projects_list: list[dict],
) -> None:
    """Save extracted projects, skipping existing ones."""
    if not projects_list:
        return

    # Remove any old projects for this resume before re-saving
    db.query(Project).filter(Project.resume_id == resume_id).delete()

    for proj in projects_list:
        if not isinstance(proj, dict):
            continue
        title = proj.get("title") or ""
        description = proj.get("description") or ""
        technologies = proj.get("technologies") or []

        if not title and not description:
            continue

        db.add(Project(
            resume_id=resume_id,
            title=title[:200] if title else None,
            description=description or None,
            technologies=[str(t) for t in technologies] if technologies else [],
        ))

    db.flush()
    logger.info("Projects saved for resume %d (%d entries)", resume_id, len(projects_list))


def _normalize_skill_name(name: str) -> str:
    """Clean and normalize a skill name."""
    if not name or not isinstance(name, str):
        return ""
    name = name.strip()
    if len(name) > 100 or len(name) < 1:
        return ""
    return name
