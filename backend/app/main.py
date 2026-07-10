"""
ResumeAtlas — FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine
from app.models import Base  # noqa: F401 — import all models so metadata is populated
from app.api.routes import crawl, resumes, search, files, pipeline

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (Alembic handles migrations in prod)
    Base.metadata.create_all(bind=engine)

    # Initialize Qdrant collection
    try:
        from app.vector_store import ensure_collection
        ensure_collection()
        logger.info("Qdrant collection ready.")
    except Exception as exc:
        logger.warning("Qdrant not available at startup (will retry on use): %s", exc)

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    description="ResumeAtlas — Discover anonymized resumes powered by AI",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(crawl.router,     prefix="/api/crawl",    tags=["crawl"])
app.include_router(resumes.router,   prefix="/api/resumes",  tags=["resumes"])
app.include_router(search.router,    prefix="/api/search",   tags=["search"])
app.include_router(files.router,     prefix="/api/files",    tags=["files"])
app.include_router(pipeline.router,  prefix="/api/pipeline", tags=["pipeline"])


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "version": settings.app_version}
