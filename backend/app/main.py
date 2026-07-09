"""
ResumeAtlas — FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine
from app.models import Base  # noqa: F401 — import all models so metadata is populated
from app.api.routes import crawl, resumes

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (Alembic handles migrations in prod)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crawl.router, prefix="/api/crawl", tags=["crawl"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["resumes"])


@app.get("/health")
def health():
    return {"status": "ok", "version": settings.app_version}
