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
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "resume_atlas"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ── Qdrant ───────────────────────────────────────
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # ── Redis ────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Gemini AI ────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # ── SocialCrawl (Reddit proxy) ───────────────────
    socialcrawl_api_key: str = ""  # Get free key at https://www.socialcrawl.dev
    target_subreddits: list[str] = Field(
        default=["EngineeringResumes", "resumes", "developersIndia"]
    )

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
