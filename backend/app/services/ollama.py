import httpx

from app.core.config import get_settings


def build_prompt(question: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(
        f"[Source {index + 1}]\n{chunk}" for index, chunk in enumerate(context_chunks)
    )
    return f"""
You are DocSense AI, an internal enterprise document intelligence assistant.
Answer the user's question using only the provided context.
If the context does not contain the answer, say that the uploaded documents do not provide enough information.
Keep the answer concise and cite source numbers inline when useful.

Context:
{context}

Question:
{question}
""".strip()


async def generate_answer(question: str, context_chunks: list[str]) -> str:
    settings = get_settings()
    prompt = build_prompt(question, context_chunks)

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
    except httpx.HTTPError as exc:
        return (
            "Retrieved relevant document context, but Ollama is not available "
            f"or the model could not generate an answer: {exc}"
        )

    payload = response.json()
    return str(payload.get("response", "")).strip() or "No answer was generated."
