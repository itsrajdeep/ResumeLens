"""
Text Extractor — Phase 5
Extracts raw text from resume files (PDF or image).

Strategy:
  1. For PDFs: use PyMuPDF (fitz) to extract embedded text.
     If the extracted text is too short (scanned/image PDF), fall back to OCR.
  2. For images: go directly to OCR.
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_MIN_TEXT_LENGTH = 100  # chars — below this, PDF is likely scanned


def extract_text_from_file(file_path: str, file_type: str) -> str:
    """
    Extract text from a resume file.

    Args:
        file_path: Absolute path to the file.
        file_type: 'pdf', 'png', 'jpg', or 'jpeg'.

    Returns:
        Extracted text string (may be empty on failure).
    """
    path = Path(file_path)
    if not path.exists():
        logger.warning("File not found: %s", file_path)
        return ""

    if file_type == "pdf":
        text = _extract_pdf_text(path)
        if len(text.strip()) >= _MIN_TEXT_LENGTH:
            logger.info("PDF text extraction succeeded (%d chars): %s", len(text), path.name)
            return text.strip()
        logger.info("PDF has insufficient text (%d chars), falling back to OCR: %s", len(text), path.name)

    # Image path (or scanned PDF fallback)
    return _extract_via_ocr(path)


def _extract_pdf_text(path: Path) -> str:
    """Use PyMuPDF to extract embedded text from a PDF."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(path))
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text())
        doc.close()
        return "\n".join(pages_text)
    except Exception as exc:
        logger.error("PyMuPDF extraction failed for %s: %s", path.name, exc)
        return ""


def _extract_via_ocr(path: Path) -> str:
    """Use EasyOCR to extract text from an image or scanned PDF page."""
    try:
        from app.pipeline.ocr import run_ocr
        return run_ocr(str(path))
    except Exception as exc:
        logger.error("OCR extraction failed for %s: %s", path.name, exc)
        return ""
