"""Shared crawler contracts."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class CrawlerArticle:
    """A normalized article returned by a crawler."""

    source_type: str
    source_name: str
    url: str
    title: str
    content: str
    cleaned_content: str
    published_at: datetime | None = None
    extra_metadata: dict[str, str] = field(default_factory=dict)


class Crawler(Protocol):
    """Protocol implemented by crawler adapters."""

    def crawl(self, source_url: str) -> list[CrawlerArticle]:
        """Collect articles from a source URL."""

