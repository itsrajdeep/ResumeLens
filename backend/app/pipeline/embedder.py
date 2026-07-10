"""
Embedder — Phase 9
Generates sentence embeddings from resume text using sentence-transformers.

Model: all-MiniLM-L6-v2
  - 22M params, 384-dim output
  - Fast, well-suited for semantic similarity
  - Runs on CPU without GPU
"""
import logging

logger = logging.getLogger(__name__)

_model = None
_MODEL_NAME = "all-MiniLM-L6-v2"


def _get_model():
    """Return a cached SentenceTransformer model instance."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: %s (first-time download may take a minute)...", _MODEL_NAME)
        _model = SentenceTransformer(_MODEL_NAME)
        logger.info("Embedding model ready.")
    return _model


def generate_embedding(text: str) -> list[float] | None:
    """
    Generate a 384-dim embedding vector from text.

    Args:
        text: Input text (resume summary or OCR text, capped at 512 tokens internally).

    Returns:
        List of 384 floats, or None on failure.
    """
    if not text or len(text.strip()) < 10:
        logger.warning("Text too short to embed (%d chars)", len(text or ""))
        return None

    try:
        model = _get_model()
        # Truncate to ~2000 chars to stay within model token limits
        truncated = text[:2000]
        embedding = model.encode(truncated, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as exc:
        logger.error("Embedding generation failed: %s", exc)
        return None
