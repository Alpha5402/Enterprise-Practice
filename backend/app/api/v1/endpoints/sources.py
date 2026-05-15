"""Source configuration API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.source_config import SourceConfigCreate, SourceConfigRead
from app.services.competitor_service import CompetitorService
from app.services.source_config_service import SourceConfigService

router = APIRouter(prefix="/sources")
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[SourceConfigRead])
def list_sources(
    db: DbSession,
    competitor_id: Annotated[UUID | None, Query()] = None,
) -> list[SourceConfigRead]:
    """List persistent source configurations."""
    return SourceConfigService(db).list_sources(competitor_id=competitor_id)


@router.post("", response_model=SourceConfigRead, status_code=status.HTTP_201_CREATED)
def create_source(payload: SourceConfigCreate, db: DbSession) -> SourceConfigRead:
    """Create a persistent source configuration."""
    competitor = CompetitorService(db).get_competitor(payload.competitor_id)
    if competitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found")
    return SourceConfigService(db).create_source(payload)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: UUID, db: DbSession) -> None:
    """Delete a persistent source configuration."""
    deleted = SourceConfigService(db).delete_source(source_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

