"""add supabase_url to resumes

Revision ID: 0002_add_supabase_url
Revises: 0001_initial_schema
Create Date: 2026-07-19
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_add_supabase_url"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "resumes",
        sa.Column("supabase_url", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("resumes", "supabase_url")
