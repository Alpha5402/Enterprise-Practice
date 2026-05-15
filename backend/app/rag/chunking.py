"""Text chunking utilities for RAG indexing."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    """A stable chunk produced from source text."""

    index: int
    text: str
    start_offset: int
    end_offset: int


class TextChunker:
    """Split source text into overlapping chunks."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        """Initialize chunking constraints."""
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[TextChunk]:
        """Split text into chunks while preserving character offsets."""
        normalized = text.strip()
        if not normalized:
            return []

        chunks: list[TextChunk] = []
        start = 0
        while start < len(normalized):
            hard_end = min(start + self.chunk_size, len(normalized))
            end = self._find_boundary(normalized, start, hard_end)
            chunk_text = normalized[start:end].strip()
            if chunk_text:
                chunks.append(
                    TextChunk(
                        index=len(chunks),
                        text=chunk_text,
                        start_offset=start,
                        end_offset=end,
                    )
                )
            if end >= len(normalized):
                break
            start = max(0, end - self.chunk_overlap)
        return chunks

    def _find_boundary(self, text: str, start: int, hard_end: int) -> int:
        """Prefer paragraph or sentence boundaries near the chunk end."""
        if hard_end >= len(text):
            return len(text)
        boundary_floor = start + max(self.chunk_size // 2, 1)
        for marker in ("\n\n", ". ", "! ", "? ", "。", "！", "？", "\n", " "):
            boundary = text.rfind(marker, boundary_floor, hard_end)
            if boundary != -1:
                return boundary + len(marker)
        return hard_end

