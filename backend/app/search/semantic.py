"""
Semantic Search — Phase 10
Qdrant-based similarity search using sentence-transformer embeddings.
"""
import logging
from typing import Any

from app.pipeline.embedder import generate_embedding
from app import vector_store

logger = logging.getLogger(__name__)


def semantic_search(
    query: str,
    limit: int = 20,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search for semantically similar resumes using Qdrant.

    Args:
        query: Natural language search query.
        limit: Max results to return.
        category: Optional category filter.

    Returns:
        List of dicts: {resume_id, score, category, summary}.
    """
    query_vector = generate_embedding(query)
    if not query_vector:
        logger.warning("Could not generate embedding for query: %s", query[:50])
        return []

    try:
        hits = vector_store.search_similar(
            query_vector=query_vector,
            limit=limit,
            category_filter=category,
        )
        return [
            {
                "id": hit["resume_id"],
                "score": hit["score"],
                "category": hit["payload"].get("category"),
                "summary": hit["payload"].get("summary", ""),
                "skills": [],
            }
            for hit in hits
        ]
    except Exception as exc:
        logger.error("Semantic search failed: %s", exc)
        return []
