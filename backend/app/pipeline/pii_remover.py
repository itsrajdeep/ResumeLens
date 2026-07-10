"""
PII Remover — Phase 7
Removes personally identifiable information from resume text using Gemini AI.

PII removed:
  - Full names
  - Email addresses
  - Phone numbers
  - Physical addresses
  - LinkedIn / GitHub / personal URLs
  - Any other identifying information

Replacements use generic placeholders:
  - Names → [NAME]
  - Emails → [EMAIL]
  - Phones → [PHONE]
  - URLs   → [URL]
  - Addresses → [ADDRESS]
"""
import logging
import re
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_PII_PROMPT = """
You are a privacy expert. Remove all personally identifiable information (PII) from the following resume text.

Replace PII with these placeholders:
- Full names → [NAME]
- Email addresses → [EMAIL]
- Phone numbers → [PHONE]
- Physical addresses (street, city, zip) → [ADDRESS]
- Personal website URLs → [URL]
- LinkedIn profile URLs → [LINKEDIN]
- GitHub profile URLs → [GITHUB]
- Any other direct identifiers → [REDACTED]

Rules:
- Keep all professional information intact (companies, job titles, universities, skills, projects)
- Keep technology names, tools, and frameworks unchanged
- Keep dates and years (e.g., "2022–2024") unchanged
- Do NOT remove company names, university names, or project names
- Return ONLY the cleaned text with no explanation

Resume text to anonymize:
"""

# Regex fallback patterns (applied after Gemini, belt-and-suspenders)
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.IGNORECASE)
_PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}"
)
_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:linkedin\.com|github\.com)/\S+",
    re.IGNORECASE,
)


def remove_pii_from_text(text: str) -> str:
    """
    Remove PII from text using Gemini AI with regex fallback.

    Args:
        text: Raw or partially processed resume text.

    Returns:
        Anonymized text string.
    """
    if not text or len(text.strip()) < 10:
        return text or ""

    anonymized = _gemini_remove_pii(text)
    if not anonymized:
        # Gemini failed — apply regex-only fallback
        logger.warning("Gemini PII removal failed, applying regex fallback")
        anonymized = text

    # Belt-and-suspenders regex cleanup
    anonymized = _EMAIL_RE.sub("[EMAIL]", anonymized)
    anonymized = _PHONE_RE.sub("[PHONE]", anonymized)
    anonymized = _URL_RE.sub("[URL]", anonymized)

    return anonymized.strip()


def anonymize_parsed_data(parsed_data: dict[str, Any]) -> dict[str, Any]:
    """
    Anonymize the structured parsed_data dict from the parser.
    Specifically nulls out the name field.

    Args:
        parsed_data: Parsed resume dict from parser.py.

    Returns:
        Anonymized copy of parsed_data.
    """
    if not parsed_data:
        return parsed_data

    result = parsed_data.copy()
    result["name"] = None  # Always null — never expose in API

    # Scrub name from summary if present
    if parsed_data.get("name") and parsed_data.get("summary"):
        name = parsed_data["name"]
        result["summary"] = result["summary"].replace(name, "[NAME]")

    return result


def _gemini_remove_pii(text: str) -> str | None:
    """Call Gemini to remove PII from text."""
    if not settings.gemini_api_key:
        logger.error("GEMINI_API_KEY not set — skipping AI PII removal")
        return None

    try:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        prompt = _PII_PROMPT + text[:8000]

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )

        result = response.text.strip()
        logger.info("PII removal: input=%d chars, output=%d chars", len(text), len(result))
        return result

    except Exception as exc:
        logger.error("Gemini PII removal failed: %s", exc)
        return None
