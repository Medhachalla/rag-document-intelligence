from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    text: str
    page_number: int | None


def chunk_pages(
    pages: list[dict[str, int | str]],
    chunk_size: int,
    chunk_overlap: int,
) -> list[TextChunk]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[TextChunk] = []
    for page in pages:
        text = str(page["text"])
        page_number = int(page["page_number"])
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(TextChunk(text=chunk_text, page_number=page_number))
            if end == len(text):
                break
            start = end - chunk_overlap

    return chunks
