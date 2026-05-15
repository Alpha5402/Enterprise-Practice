"""API router composition."""

from fastapi import APIRouter

from app.api.v1.endpoints import competitors, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(competitors.router, tags=["competitors"])

