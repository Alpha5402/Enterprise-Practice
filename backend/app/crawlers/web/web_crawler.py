"""News webpage crawler implementation."""

import httpx
from bs4 import BeautifulSoup

from app.crawlers.base import CrawlerArticle
from app.crawlers.text_cleaner import TextCleaner


class WebCrawler:
    """Collect article-like content from public web pages."""

    def __init__(
        self,
        client: httpx.Client | None = None,
        cleaner: TextCleaner | None = None,
    ) -> None:
        """Initialize the crawler with injectable HTTP and cleaning dependencies."""
        self.client = client or httpx.Client(timeout=15.0, follow_redirects=True)
        self.cleaner = cleaner or TextCleaner()

    def crawl(self, source_url: str) -> list[CrawlerArticle]:
        """Fetch a webpage and return a single normalized article record."""
        response = self.client.get(source_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for removable in soup(["script", "style", "noscript", "svg"]):
            removable.decompose()

        title = self._title(soup, source_url)
        content = self._content(soup)
        cleaned_content = self.cleaner.clean(content)
        if not cleaned_content:
            return []

        return [
            CrawlerArticle(
                source_type="web",
                source_name=self._source_name(soup, source_url),
                url=str(response.url),
                title=title,
                content=content,
                cleaned_content=cleaned_content,
                extra_metadata={"requested_url": source_url},
            )
        ]

    def _title(self, soup: BeautifulSoup, fallback: str) -> str:
        """Extract a human-readable page title."""
        heading = soup.find("h1")
        if heading and heading.get_text(strip=True):
            return self.cleaner.clean(heading.get_text(" "))
        if soup.title and soup.title.get_text(strip=True):
            return self.cleaner.clean(soup.title.get_text(" "))
        return fallback

    def _content(self, soup: BeautifulSoup) -> str:
        """Extract article body text from semantic containers or page body."""
        container = soup.find("article") or soup.find("main") or soup.body or soup
        return container.get_text(" ")

    def _source_name(self, soup: BeautifulSoup, fallback: str) -> str:
        """Extract source name from metadata when available."""
        site_name = soup.find("meta", property="og:site_name")
        if site_name and site_name.get("content"):
            return self.cleaner.clean(str(site_name["content"]))
        return fallback
