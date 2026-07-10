"""
Resume Parser — Phase 6
Uses Gemini AI to parse raw resume text into structured data.

Output format (stored as JSONB in parsed_data):
{
  "name": "...",          # anonymized to null by PII remover later
  "summary": "...",       # 2-3 sentence professional summary
  "category": "...",      # Frontend | Backend | AI/ML | DevOps | Data | Mobile | Full-Stack | Other
  "experience_years": 2,  # estimated years of experience
  "education": [
    {"degree": "B.Tech", "field": "Computer Science", "institution": "...", "year": 2022}
  ],
  "experience": [
    {"title": "...", "company": "...", "duration": "...", "highlights": ["..."]}
  ],
  "skills": {
    "languages": ["Python", "JavaScript"],
    "frameworks": ["FastAPI", "React"],
    "databases": ["PostgreSQL", "Redis"],
    "cloud": ["AWS", "GCP"],
    "tools": ["Docker", "Git", "CI/CD"]
  },
  "projects": [
    {"title": "...", "description": "...", "technologies": ["..."]}
  ]
}
"""
import json
import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_PARSE_PROMPT = """
You are a resume data extraction expert. Parse the following resume text and extract structured information.

Return ONLY valid JSON with this exact schema (no markdown, no explanation):
{
  "name": "full name or null",
  "summary": "2-3 sentence professional summary describing this person's background and expertise",
  "category": "one of: Frontend | Backend | AI/ML | DevOps | Data | Mobile | Full-Stack | Other",
  "experience_years": <integer or null>,
  "education": [
    {"degree": "degree name", "field": "field of study", "institution": "university name", "year": <year or null>}
  ],
  "experience": [
    {"title": "job title", "company": "company name", "duration": "e.g. Jan 2022 - Mar 2024", "highlights": ["bullet point 1", "bullet point 2"]}
  ],
  "skills": {
    "languages": ["list of programming languages"],
    "frameworks": ["list of frameworks and libraries"],
    "databases": ["list of databases"],
    "cloud": ["list of cloud platforms and services"],
    "tools": ["list of tools, platforms, methodologies"]
  },
  "projects": [
    {"title": "project name", "description": "brief description", "technologies": ["tech1", "tech2"]}
  ]
}

Rules:
- Normalize skill names (e.g., "JS" → "JavaScript", "Py" → "Python", "k8s" → "Kubernetes")
- If a field is not present, use null or empty array []
- For category, choose the most dominant role based on skills and experience
- Keep all text clean and professional

Resume text:
"""


def parse_resume(ocr_text: str) -> dict[str, Any] | None:
    """
    Parse raw resume text using Gemini AI.

    Args:
        ocr_text: Raw text extracted from the resume file.

    Returns:
        Parsed resume dict or None on failure.
    """
    if not ocr_text or len(ocr_text.strip()) < 50:
        logger.warning("Text too short to parse (%d chars)", len(ocr_text or ""))
        return None

    if not settings.gemini_api_key:
        logger.error("GEMINI_API_KEY not set — skipping AI parsing")
        return None

    try:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        prompt = _PARSE_PROMPT + ocr_text[:8000]  # cap at ~8k chars

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )

        raw = response.text.strip()

        # Strip markdown code fences if Gemini wraps the JSON
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        parsed = json.loads(raw)
        logger.info("Resume parsed: category=%s, skills=%d",
                    parsed.get("category"), _count_skills(parsed.get("skills", {})))
        return parsed

    except json.JSONDecodeError as exc:
        logger.error("Gemini returned invalid JSON: %s", exc)
        return None
    except Exception as exc:
        logger.error("Gemini parse failed: %s", exc)
        return None


def _count_skills(skills: dict) -> int:
    return sum(len(v) for v in skills.values() if isinstance(v, list))
