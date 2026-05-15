"""API router composition."""

from fastapi import APIRouter

from app.api.v1.endpoints import competitors, health, rag, reports

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(competitors.router, tags=["competitors"])
api_router.include_router(reports.router, tags=["reports"])
api_router.include_router(rag.router, tags=["rag"])
