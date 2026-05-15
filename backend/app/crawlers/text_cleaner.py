"""Text normalization helpers for crawler output."""

import re
from html import unescape

_WHITESPACE_PATTERN = re.compile(r"\s+")


class TextCleaner:
    """Clean raw crawled text into retrieval-ready content."""

    def clean(self, text: str) -> str:
        """Normalize escaped text, repeated whitespace, and empty lines."""
        normalized = unescape(text)
        normalized = normalized.replace("\x00", " ")
        normalized = _WHITESPACE_PATTERN.sub(" ", normalized)
        return normalized.strip()

