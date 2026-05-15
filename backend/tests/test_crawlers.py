"""Crawler behavior tests."""

import httpx

from app.crawlers.rss.rss_crawler import RssCrawler
from app.crawlers.text_cleaner import TextCleaner
from app.crawlers.web.web_crawler import WebCrawler


def test_text_cleaner_normalizes_whitespace() -> None:
    """Text cleaner collapses noisy crawler whitespace."""
    assert TextCleaner().clean("  Alpha\n\n&nbsp; Beta\t ") == "Alpha Beta"


def test_rss_crawler_parses_feed() -> None:
    """RSS crawler parses feed entries into normalized articles."""
    feed = """<?xml version="1.0"?>
    <rss version="2.0">
      <channel>
        <title>Market Feed</title>
        <item>
          <title>Acme cuts prices</title>
          <link>https://example.com/acme-pricing</link>
          <description>Acme reduced entry pricing.</description>
          <pubDate>Fri, 15 May 2026 12:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=feed.encode("utf-8"))

    crawler = RssCrawler(client=httpx.Client(transport=httpx.MockTransport(handler)))
    articles = crawler.crawl("https://example.com/feed.xml")

    assert len(articles) == 1
    assert articles[0].source_type == "rss"
    assert articles[0].title == "Acme cuts prices"


def test_web_crawler_extracts_article_text() -> None:
    """Web crawler extracts title and article body from HTML."""
    html = """
    <html>
      <head><meta property="og:site_name" content="Market News"><title>Fallback</title></head>
      <body>
        <article>
          <h1>Acme launches platform</h1>
          <p>New product line announced.</p>
        </article>
      </body>
    </html>
    """

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=html, request=httpx.Request("GET", "https://example.com/news"))

    crawler = WebCrawler(client=httpx.Client(transport=httpx.MockTransport(handler)))
    articles = crawler.crawl("https://example.com/news")

    assert len(articles) == 1
    assert articles[0].source_name == "Market News"
    assert articles[0].title == "Acme launches platform"
    assert "New product line announced." in articles[0].cleaned_content
