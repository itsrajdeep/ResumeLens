"""
Resume model — Represents a processed and anonymized resume.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    raw_file_path = Column(Text, nullable=False)
    anonymous_file_path = Column(Text)
    supabase_url = Column(Text)          # Permanent public URL on Supabase Storage
    ocr_text = Column(Text)
    parsed_data = Column(JSONB)  # Structured resume data from Gemini
    summary = Column(Text)
    file_hash = Column(String(64), unique=True, index=True)  # SHA256 dedup
    category = Column(String(50), index=True)  # frontend, backend, AI, etc.
    embedding_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    post = relationship("Post", back_populates="resumes")
    skills = relationship("ResumeSkill", back_populates="resume", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="resume", cascade="all, delete-orphan")

    # Full-text search index is created via Alembic migration

    def __repr__(self):
        return f"<Resume(id={self.id}, category={self.category})>"
