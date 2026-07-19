"""
ResumeAtlas Configuration — Loads settings from environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # ── App ──────────────────────────────────────────
    app_name: str = "ResumeAtlas"
    app_version: str = "0.1.0"
    debug: bool = True

    # ── PostgreSQL ───────────────────────────────────
    # On Koyeb/prod: set DATABASE_URL directly. On local Docker: built from parts.
    database_url_override: str = Field(default="", alias="DATABASE_URL", validation_alias="DATABASE_URL")
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "resume_atlas"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ── Qdrant ───────────────────────────────────────
    qdrant_host: str = "qdrant"   # Docker service name; override on prod
    qdrant_port: int = 6333
    qdrant_api_key: str = ""

    # ── Redis ────────────────────────────────────────
    redis_url: str = "redis://redis:6379/0"  # Docker service name; override on prod

    # ── Gemini AI ────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # ── SocialCrawl (Reddit proxy) ───────────────────
    socialcrawl_api_key: str = ""  # Get free key at https://www.socialcrawl.dev
    target_subreddits: list[str] = Field(
        default=["EngineeringResumes", "resumes", "developersIndia"]
    )

    # ── Supabase Storage ─────────────────────────────
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_bucket: str = "resumes"

    # ── Storage ──────────────────────────────────────
    storage_path: str = "./storage"

    @property
    def raw_storage_path(self) -> str:
        return f"{self.storage_path}/raw"

    @property
    def anonymous_storage_path(self) -> str:
        return f"{self.storage_path}/anonymous"

    # ── Backend ──────────────────────────────────────
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
