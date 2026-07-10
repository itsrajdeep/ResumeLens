"""
Vector Store — Phase 9
Qdrant client singleton with upsert and search helpers.

Collection: "resumes"
  - Vector: 384-dim (all-MiniLM-L6-v2)
  - Payload: {resume_id, category, summary}
"""
import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_COLLECTION_NAME = "resumes"
_VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension

_client = None


def _get_client():
    """Return a cached Qdrant client."""
    global _client
    if _client is None:
        from qdrant_client import QdrantClient
        _client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            timeout=10,
        )
        logger.info("Qdrant client connected to %s:%d", settings.qdrant_host, settings.qdrant_port)
    return _client


def ensure_collection() -> None:
    """Create the Qdrant collection if it doesn't exist."""
    from qdrant_client.models import Distance, VectorParams

    client = _get_client()
    existing = [c.name for c in client.get_collections().collections]

    if _COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=_COLLECTION_NAME,
            vectors_config=VectorParams(size=_VECTOR_SIZE, distance=Distance.COSINE),
        )
        logger.info("Created Qdrant collection: %s", _COLLECTION_NAME)
    else:
        logger.debug("Qdrant collection already exists: %s", _COLLECTION_NAME)


def upsert_resume(resume_id: int, vector: list[float], payload: dict[str, Any]) -> str:
    """
    Upsert a resume vector into Qdrant.

    Args:
        resume_id: Database ID (used as Qdrant point ID).
        vector: 384-dim embedding vector.
        payload: Metadata dict stored alongside the vector.

    Returns:
        Qdrant point ID as string.
    """
    from qdrant_client.models import PointStruct

    client = _get_client()
    ensure_collection()

    point = PointStruct(id=resume_id, vector=vector, payload=payload)
    client.upsert(collection_name=_COLLECTION_NAME, points=[point])
    logger.debug("Upserted resume %d into Qdrant", resume_id)
    return str(resume_id)


def search_similar(
    query_vector: list[float],
    limit: int = 20,
    category_filter: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search for similar resumes by vector.

    Args:
        query_vector: Query embedding vector.
        limit: Number of results.
        category_filter: Optional category to filter by.

    Returns:
        List of dicts with {resume_id, score, payload}.
    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    client = _get_client()

    query_filter = None
    if category_filter:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="category",
                    match=MatchValue(value=category_filter),
                )
            ]
        )

    response = client.query_points(
        collection_name=_COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        query_filter=query_filter,
        with_payload=True,
    )

    return [
        {
            "resume_id": int(hit.id),
            "score": hit.score,
            "payload": hit.payload,
        }
        for hit in response.points
    ]
