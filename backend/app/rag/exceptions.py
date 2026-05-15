"""RAG-specific exceptions."""


class RagConfigurationError(RuntimeError):
    """Raised when a required RAG provider is not configured."""

