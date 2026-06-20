from pathlib import Path

from pypdf import PdfReader


def extract_pdf_pages(path: Path) -> list[dict[str, int | str]]:
    reader = PdfReader(path)
    pages: list[dict[str, int | str]] = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        normalized = " ".join(text.split())
        if normalized:
            pages.append({"page_number": index, "text": normalized})

    return pages
