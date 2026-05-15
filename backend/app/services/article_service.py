"""Business operations for collected articles."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.news_article import NewsArticle
from app.schemas.news_article import NewsArticleCreate


class ArticleService:
    """Coordinate persistence operations for collected articles."""

    def __init__(self, db: Session) -> None:
        """Initialize the service with a database session."""
        self.db = db

    def list_articles(self, competitor_id: UUID | None = None) -> list[NewsArticle]:
        """Return collected articles, optionally scoped to a competitor."""
        statement = select(NewsArticle).order_by(NewsArticle.collected_at.desc())
        if competitor_id is not None:
            statement = statement.where(NewsArticle.competitor_id == competitor_id)
        return list(self.db.scalars(statement).all())

    def get_article(self, article_id: UUID) -> NewsArticle | None:
        """Return an article by id."""
        return self.db.get(NewsArticle, article_id)

    def get_by_url(self, url: str) -> NewsArticle | None:
        """Return an article by canonical URL."""
        statement = select(NewsArticle).where(NewsArticle.url == url)
        return self.db.scalar(statement)

    def create_article(self, payload: NewsArticleCreate) -> NewsArticle:
        """Create and persist a collected article."""
        article = NewsArticle(**payload.model_dump(mode="json"))
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def create_if_new(self, payload: NewsArticleCreate) -> NewsArticle:
        """Create an article unless its URL already exists."""
        existing = self.get_by_url(str(payload.url))
        if existing is not None:
            return existing
        return self.create_article(payload)
