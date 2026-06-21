from pathlib import Path

from pypdf import PdfReader

from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_pdf_pages(path: Path) -> list[dict[str, int | str]]:
    logger.info("Extracting PDF text path=%s", path)

    try:
        reader = PdfReader(path)
    except Exception:
        logger.exception("PDF extraction failed path=%s", path)
        raise

    pages: list[dict[str, int | str]] = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        normalized = " ".join(text.split())
        if normalized:
            pages.append({"page_number": index, "text": normalized})

    logger.info("PDF text extracted path=%s pages_with_text=%d", path, len(pages))
    return pages
