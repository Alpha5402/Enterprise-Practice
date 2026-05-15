"""Application service for collecting and persisting crawler output."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.crawlers.base import Crawler
from app.models.news_article import NewsArticle
from app.schemas.news_article import NewsArticleCreate
from app.services.article_service import ArticleService


class CollectionService:
    """Coordinate crawler execution and article persistence."""

    def __init__(self, db: Session) -> None:
        """Initialize the service with a database session."""
        self.article_service = ArticleService(db)

    def collect_for_competitor(
        self,
        competitor_id: UUID,
        source_url: str,
        crawler: Crawler,
    ) -> list[NewsArticle]:
        """Collect articles from a source and persist unseen URLs."""
        collected = []
        for article in crawler.crawl(source_url):
            payload = NewsArticleCreate(
                competitor_id=competitor_id,
                source_type=article.source_type,
                source_name=article.source_name,
                url=article.url,
                title=article.title,
                content=article.content,
                cleaned_content=article.cleaned_content,
                published_at=article.published_at,
                extra_metadata=article.extra_metadata,
            )
            collected.append(self.article_service.create_if_new(payload))
        return collected

