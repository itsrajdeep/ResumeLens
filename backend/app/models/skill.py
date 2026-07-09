"""
Skill model — Represents a technology skill (language, framework, tool, cloud).
ResumeSkill — Many-to-many junction table between resumes and skills.
"""
from sqlalchemy import (
    Column, Integer, String, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), index=True)  # language, framework, cloud, tool, database
    usage_count = Column(Integer, default=0)

    # Relationships
    resumes = relationship("ResumeSkill", back_populates="skill", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Skill(name={self.name}, category={self.category})>"


class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        primary_key=True
    )
    skill_id = Column(
        Integer,
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True
    )

    # Relationships
    resume = relationship("Resume", back_populates="skills")
    skill = relationship("Skill", back_populates="resumes")
