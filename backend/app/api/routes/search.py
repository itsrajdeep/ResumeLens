"""
Search API Routes — Phase 10
Hybrid keyword + semantic search endpoint.

GET /api/search?q=python+backend&mode=hybrid&category=Backend&page=1
"""
import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.search import SearchResponse, SearchResult
from app.search.keyword import keyword_search
from app.search.semantic import semantic_search

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    mode: str = Query("hybrid", description="Search mode: keyword | semantic | hybrid"),
    category: str | None = Query(None, description="Filter by resume category"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Hybrid search combining PostgreSQL full-text and Qdrant semantic search.

    Modes:
      - keyword:  PostgreSQL FTS only (fast, exact term matching)
      - semantic: Qdrant vector similarity only (natural language)
      - hybrid:   Combine and deduplicate results (default)
    """
    kw_results: list[dict] = []
    sem_results: list[dict] = []
    total = 0

    if mode in ("keyword", "hybrid"):
        kw_data = keyword_search(db, q, category=category, page=page, page_size=page_size)
        kw_results = kw_data.get("results", [])
        total = kw_data.get("total", 0)

    if mode in ("semantic", "hybrid"):
        sem_results = semantic_search(q, limit=page_size, category=category)

    if mode == "hybrid":
        results = _merge_results(kw_results, sem_results, page_size)
        total = max(total, len(results))  # approximate total
    elif mode == "semantic":
        results = sem_results
        total = len(results)
    else:
        results = kw_results

    return SearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=[
            SearchResult(
                id=r["id"],
                post_id=r.get("post_id", 0),
                category=r.get("category"),
                summary=r.get("summary"),
                skills=r.get("skills", []),
                score=r.get("score", 0.0),
            )
            for r in results
        ],
    )


def _merge_results(
    kw: list[dict],
    sem: list[dict],
    limit: int,
) -> list[dict]:
    """
    Merge keyword and semantic results, deduplicate by resume ID,
    and re-rank by combined score.
    """
    seen: dict[int, dict] = {}

    # Normalize scores to [0, 1] range within each result set
    def normalize(results: list[dict]) -> list[dict]:
        if not results:
            return results
        max_score = max(r["score"] for r in results) or 1.0
        return [{**r, "score": r["score"] / max_score} for r in results]

    for r in normalize(kw):
        rid = r["id"]
        seen[rid] = {**r, "score": r["score"] * 0.5}  # 50% weight for keyword

    for r in normalize(sem):
        rid = r["id"]
        if rid in seen:
            seen[rid]["score"] += r["score"] * 0.5  # add semantic weight
        else:
            seen[rid] = {**r, "score": r["score"] * 0.5}

    merged = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
    return merged[:limit]
