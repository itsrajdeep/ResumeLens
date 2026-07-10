"""
OCR Engine — Phase 5
Handles image-based resume text extraction using EasyOCR.

For scanned PDFs, PyMuPDF renders pages to images first, then EasyOCR processes them.
EasyOCR is chosen over PaddleOCR for simpler Docker setup (no paddle deps).
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Lazy-loaded reader (expensive to init, reuse across calls)
_reader = None


def _get_reader():
    """Return a cached EasyOCR Reader instance."""
    global _reader
    if _reader is None:
        import easyocr
        logger.info("Initializing EasyOCR reader (first-time load)...")
        _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        logger.info("EasyOCR reader ready.")
    return _reader


def run_ocr(file_path: str) -> str:
    """
    Run OCR on an image or scanned PDF and return extracted text.

    For PDFs: renders each page to an image using PyMuPDF, then OCRs each page.
    For images: OCRs directly.

    Args:
        file_path: Absolute path to the file.

    Returns:
        Concatenated text from all pages / the image.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _ocr_pdf(path)
    else:
        return _ocr_image(str(path))


def _ocr_image(image_path: str) -> str:
    """OCR a single image file."""
    try:
        reader = _get_reader()
        results = reader.readtext(image_path, detail=0, paragraph=True)
        text = "\n".join(results)
        logger.info("OCR extracted %d chars from image: %s", len(text), image_path)
        return text
    except Exception as exc:
        logger.error("EasyOCR failed for image %s: %s", image_path, exc)
        return ""


def _ocr_pdf(path: Path) -> str:
    """
    Render each PDF page to an image using PyMuPDF, then OCR.
    Used as fallback when PDF has no embedded text.
    """
    try:
        import fitz
        import tempfile
        import os

        doc = fitz.open(str(path))
        page_texts = []
        reader = _get_reader()

        for page_num, page in enumerate(doc):
            # Render at 2x zoom for better OCR accuracy
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
                pix.save(tmp_path)

            try:
                results = reader.readtext(tmp_path, detail=0, paragraph=True)
                page_texts.append("\n".join(results))
                logger.debug("OCR page %d: %d chars", page_num + 1, len(page_texts[-1]))
            finally:
                os.unlink(tmp_path)

        doc.close()
        full_text = "\n\n".join(page_texts)
        logger.info("PDF OCR extracted %d chars from %s", len(full_text), path.name)
        return full_text

    except Exception as exc:
        logger.error("PDF OCR failed for %s: %s", path.name, exc)
        return ""
