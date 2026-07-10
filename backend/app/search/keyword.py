"""
Keyword Search — Phase 10
PostgreSQL full-text search over resumes using tsvector/tsquery.

Search targets: ocr_text and summary (indexed by GIN in migration 0001).
"""
import logging
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


def keyword_search(
    db: Session,
    query: str,
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """
    Full-text search using PostgreSQL tsvector ranking.

    Args:
        db: Database session.
        query: Search query string.
        category: Optional category filter.
        page: 1-indexed page number.
        page_size: Results per page.

    Returns:
        Dict with {total, results} where results contain resume rows + rank score.
    """
    offset = (page - 1) * page_size

    # Build parameterized query
    base_conditions = "r.ocr_text IS NOT NULL"
    params: dict[str, Any] = {
        "query": query,
        "limit": page_size,
        "offset": offset,
    }

    if category:
        base_conditions += " AND r.category = :category"
        params["category"] = category

    sql = text(f"""
        SELECT
            r.id,
            r.post_id,
            r.category,
            r.summary,
            r.embedding_id,
            r.created_at,
            ts_rank_cd(
                to_tsvector('english', COALESCE(r.ocr_text, '') || ' ' || COALESCE(r.summary, '')),
                plainto_tsquery('english', :query)
            ) AS rank
        FROM resumes r
        WHERE {base_conditions}
          AND to_tsvector('english', COALESCE(r.ocr_text, '') || ' ' || COALESCE(r.summary, ''))
              @@ plainto_tsquery('english', :query)
        ORDER BY rank DESC
        LIMIT :limit OFFSET :offset
    """)

    count_sql = text(f"""
        SELECT COUNT(*) FROM resumes r
        WHERE {base_conditions}
          AND to_tsvector('english', COALESCE(r.ocr_text, '') || ' ' || COALESCE(r.summary, ''))
              @@ plainto_tsquery('english', :query)
    """)

    count_params = {k: v for k, v in params.items() if k not in ("limit", "offset")}

    try:
        total = db.execute(count_sql, count_params).scalar() or 0
        rows = db.execute(sql, params).fetchall()
    except Exception as exc:
        logger.error("Keyword search failed: %s", exc)
        return {"total": 0, "results": []}

    results = [
        {
            "id": row.id,
            "post_id": row.post_id,
            "category": row.category,
            "summary": row.summary,
            "score": float(row.rank),
            "skills": [],  # populated by caller if needed
        }
        for row in rows
    ]

    logger.info("Keyword search '%s': %d results (total=%d)", query, len(results), total)
    return {"total": total, "results": results}
