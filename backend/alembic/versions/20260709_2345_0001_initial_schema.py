"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-07-09 23:45:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── posts ───────────────────────────────────────────────────────────
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reddit_id", sa.String(20), nullable=False),
        sa.Column("subreddit", sa.String(50), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("author", sa.String(50), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("permalink", sa.Text(), nullable=True),
        sa.Column("file_url", sa.Text(), nullable=True),
        sa.Column("file_type", sa.String(10), nullable=True),
        sa.Column("processed", sa.Boolean(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.Column("last_checked", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reddit_id"),
    )
    op.create_index("ix_posts_reddit_id", "posts", ["reddit_id"])
    op.create_index("ix_posts_subreddit", "posts", ["subreddit"])

    # ── resumes ─────────────────────────────────────────────────────────
    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("raw_file_path", sa.Text(), nullable=False),
        sa.Column("anonymous_file_path", sa.Text(), nullable=True),
        sa.Column("ocr_text", sa.Text(), nullable=True),
        sa.Column("parsed_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("embedding_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_hash"),
    )
    op.create_index("ix_resumes_category", "resumes", ["category"])
    op.create_index("ix_resumes_file_hash", "resumes", ["file_hash"])
    # Full-text search index
    op.execute(
        "CREATE INDEX idx_resumes_fts ON resumes "
        "USING GIN (to_tsvector('english', "
        "COALESCE(ocr_text, '') || ' ' || COALESCE(summary, '')))"
    )

    # ── skills ──────────────────────────────────────────────────────────
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("usage_count", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_skills_name", "skills", ["name"])
    op.create_index("ix_skills_category", "skills", ["category"])

    # ── resume_skills ────────────────────────────────────────────────────
    op.create_table(
        "resume_skills",
        sa.Column("resume_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("resume_id", "skill_id"),
    )

    # ── projects ─────────────────────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("resume_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("technologies", postgresql.ARRAY(sa.String()), nullable=True),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── sync_state ───────────────────────────────────────────────────────
    op.create_table(
        "sync_state",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("subreddit", sa.String(50), nullable=False),
        sa.Column("last_post_id", sa.String(20), nullable=True),
        sa.Column("last_sync_at", sa.DateTime(), nullable=True),
        sa.Column("total_posts_synced", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("subreddit"),
    )


def downgrade() -> None:
    op.drop_table("sync_state")
    op.drop_table("projects")
    op.drop_table("resume_skills")
    op.drop_index("ix_skills_category", table_name="skills")
    op.drop_index("ix_skills_name", table_name="skills")
    op.drop_table("skills")
    op.execute("DROP INDEX IF EXISTS idx_resumes_fts")
    op.drop_index("ix_resumes_file_hash", table_name="resumes")
    op.drop_index("ix_resumes_category", table_name="resumes")
    op.drop_table("resumes")
    op.drop_index("ix_posts_subreddit", table_name="posts")
    op.drop_index("ix_posts_reddit_id", table_name="posts")
    op.drop_table("posts")
