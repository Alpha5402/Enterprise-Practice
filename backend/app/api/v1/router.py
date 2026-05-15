"""API router composition."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    analysis,
    articles,
    automation,
    collection,
    competitors,
    health,
    rag,
    reports,
    sources,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(competitors.router, tags=["competitors"])
api_router.include_router(articles.router, tags=["articles"])
api_router.include_router(automation.router, tags=["automation"])
api_router.include_router(collection.router, tags=["collection"])
api_router.include_router(sources.router, tags=["sources"])
api_router.include_router(reports.router, tags=["reports"])
api_router.include_router(rag.router, tags=["rag"])
api_router.include_router(analysis.router, tags=["analysis"])
