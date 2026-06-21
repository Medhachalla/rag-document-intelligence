from app.services.ollama import build_prompt, format_source_context


def test_format_source_context_includes_file_page_and_content() -> None:
    context = format_source_context(
        filename="Actuators.pdf",
        page_number=3,
        content="Actuators are used to move or control mechanisms.",
    )

    assert "[Source]" in context
    assert "File:\nActuators.pdf" in context
    assert "Page:\n3" in context
    assert "Content:\nActuators are used" in context


def test_build_prompt_preserves_structured_sources() -> None:
    context = format_source_context(
        filename="Actuators.pdf",
        page_number=3,
        content="Actuators are used to move or control mechanisms.",
    )

    prompt = build_prompt("What are actuators used for?", [context])

    assert "cite file names and page numbers" in prompt
    assert "File:\nActuators.pdf" in prompt
    assert "Page:\n3" in prompt
