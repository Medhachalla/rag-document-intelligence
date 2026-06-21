import httpx

from app.core.config import get_settings
from app.core.exceptions import OllamaModelError, OllamaTimeoutError, OllamaUnavailableError
from app.core.logging import get_logger

logger = get_logger(__name__)


def format_source_context(
    *,
    filename: str,
    page_number: int | None,
    content: str,
) -> str:
    page = "Unknown" if page_number is None else str(page_number)
    return f"""
[Source]
File:
{filename}

Page:
{page}

Content:
{content}
""".strip()


def build_prompt(question: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(context_chunks)
    return f"""
You are DocSense AI, an internal enterprise document intelligence assistant.
Answer the user's question using only the provided context.
If the context does not contain the answer, say that the uploaded documents do not provide enough information.
Keep the answer concise and cite file names and page numbers inline when useful.
Rules:
- Include every relevant item from the source.
- Do not omit categories, numbers, or lists.
- If the answer is explicitly present in the document, copy the structure.

Context:
{context}

Question:
{question}

Answer:

"""

async def generate_answer(question: str, context_chunks: list[str]) -> str:
    settings = get_settings()
    prompt = build_prompt(question, context_chunks)

    logger.info(
        "Ollama generation started model=%s context_chunks=%d",
        settings.ollama_model,
        len(context_chunks),
    )

    try:
        async with httpx.AsyncClient(timeout=settings.ollama_timeout_seconds) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        logger.error("Ollama request timed out model=%s", settings.ollama_model)
        raise OllamaTimeoutError() from exc
    except httpx.ConnectError as exc:
        logger.error("Ollama service unavailable url=%s", settings.ollama_base_url)
        raise OllamaUnavailableError() from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            logger.error("Ollama model not found model=%s", settings.ollama_model)
            raise OllamaModelError() from exc
        logger.error(
            "Ollama request failed model=%s status=%d",
            settings.ollama_model,
            exc.response.status_code,
        )
        raise OllamaUnavailableError(
            "Unable to generate answer. Ollama returned an error."
        ) from exc
    except httpx.HTTPError as exc:
        logger.error("Ollama request failed model=%s", settings.ollama_model)
        raise OllamaUnavailableError() from exc

    payload = response.json()
    answer = str(payload.get("response", "")).strip()
    if not answer:
        logger.error("Ollama returned empty response model=%s", settings.ollama_model)
        raise OllamaUnavailableError("Ollama did not return an answer.")

    logger.info("Ollama generation completed model=%s", settings.ollama_model)
    return answer
