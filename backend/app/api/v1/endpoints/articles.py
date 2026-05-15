"""Collected article API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.news_article import NewsArticleRead
from app.services.article_service import ArticleService

router = APIRouter(prefix="/articles")
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[NewsArticleRead])
def list_articles(
    db: DbSession,
    competitor_id: Annotated[UUID | None, Query()] = None,
) -> list[NewsArticleRead]:
    """List collected articles, optionally scoped to one competitor."""
    return ArticleService(db).list_articles(competitor_id=competitor_id)

