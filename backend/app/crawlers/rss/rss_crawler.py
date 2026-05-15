"""RSS feed crawler implementation."""

from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from app.crawlers.base import CrawlerArticle
from app.crawlers.text_cleaner import TextCleaner


class RssCrawler:
    """Collect articles from RSS or Atom feeds."""

    def __init__(
        self,
        client: httpx.Client | None = None,
        cleaner: TextCleaner | None = None,
    ) -> None:
        """Initialize the crawler with injectable HTTP and cleaning dependencies."""
        self.client = client or httpx.Client(timeout=15.0, follow_redirects=True)
        self.cleaner = cleaner or TextCleaner()

    def crawl(self, source_url: str) -> list[CrawlerArticle]:
        """Fetch and parse a feed URL into normalized article records."""
        response = self.client.get(source_url)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        source_name = feed.feed.get("title", source_url)
        articles: list[CrawlerArticle] = []

        for entry in feed.entries:
            url = entry.get("link", "")
            title = self.cleaner.clean(entry.get("title", "Untitled"))
            raw_content = self._entry_content(entry)
            cleaned_content = self.cleaner.clean(raw_content)
            if not url or not cleaned_content:
                continue
            articles.append(
                CrawlerArticle(
                    source_type="rss",
                    source_name=source_name,
                    url=url,
                    title=title,
                    content=raw_content,
                    cleaned_content=cleaned_content,
                    published_at=self._published_at(entry),
                    extra_metadata={"feed_url": source_url},
                )
            )

        return articles

    def _entry_content(self, entry: feedparser.FeedParserDict) -> str:
        """Extract the best available content field from a feed entry."""
        content = entry.get("content")
        if content and isinstance(content, list):
            first = content[0]
            if isinstance(first, dict):
                return str(first.get("value", ""))
        return str(entry.get("summary", entry.get("description", "")))

    def _published_at(self, entry: feedparser.FeedParserDict) -> datetime | None:
        """Parse a feed entry publication timestamp."""
        published = entry.get("published") or entry.get("updated")
        if not published:
            return None
        try:
            parsed = parsedate_to_datetime(published)
        except (TypeError, ValueError):
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed
