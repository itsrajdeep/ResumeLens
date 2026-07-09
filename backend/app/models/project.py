"""
Project model — Represents a project extracted from a resume.
"""
from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, ARRAY
)
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(
        Integer,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False
    )
    title = Column(String(200))
    description = Column(Text)
    technologies = Column(ARRAY(String))  # PostgreSQL array of strings

    # Relationships
    resume = relationship("Resume", back_populates="projects")

    def __repr__(self):
        return f"<Project(title={self.title})>"
