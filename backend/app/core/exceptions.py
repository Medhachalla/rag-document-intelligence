from typing import Any


class DocSenseError(Exception):
    """Base domain exception mapped to structured API error responses."""

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 500,
        *,
        citations: list[Any] | None = None,
    ) -> None:
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.citations = citations
        super().__init__(message)


class InvalidFileTypeError(DocSenseError):
    def __init__(self, message: str = "Only PDF uploads are supported.") -> None:
        super().__init__("INVALID_FILE_TYPE", message, status_code=400)


class EmptyFileError(DocSenseError):
    def __init__(self, message: str = "Uploaded PDF is empty.") -> None:
        super().__init__("EMPTY_FILE", message, status_code=400)


class FileTooLargeError(DocSenseError):
    def __init__(self, max_mb: int) -> None:
        super().__init__(
            "FILE_TOO_LARGE",
            f"PDF exceeds the {max_mb} MB upload limit.",
            status_code=413,
        )


class DocumentNotFoundError(DocSenseError):
    def __init__(self, message: str = "Document not found.") -> None:
        super().__init__("DOCUMENT_NOT_FOUND", message, status_code=404)


class OllamaError(DocSenseError):
    def __init__(self, error_code: str, message: str, status_code: int = 503) -> None:
        super().__init__(error_code, message, status_code=status_code)


class OllamaUnavailableError(OllamaError):
    def __init__(
        self,
        message: str = "Unable to generate answer. Start Ollama service.",
    ) -> None:
        super().__init__("OLLAMA_UNAVAILABLE", message)


class OllamaTimeoutError(OllamaError):
    def __init__(
        self,
        message: str = "Answer generation timed out. Try again or increase the timeout.",
    ) -> None:
        super().__init__("OLLAMA_TIMEOUT", message)


class OllamaModelError(OllamaError):
    def __init__(
        self,
        message: str = "Configured Ollama model is not available.",
    ) -> None:
        super().__init__("OLLAMA_MODEL_ERROR", message)
