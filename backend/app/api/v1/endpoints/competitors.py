"""Competitor API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.competitor import CompetitorCreate, CompetitorRead
from app.services.competitor_service import CompetitorService

router = APIRouter(prefix="/competitors")
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[CompetitorRead])
def list_competitors(db: DbSession) -> list[CompetitorRead]:
    """List configured competitors."""
    return CompetitorService(db).list_competitors()


@router.post("", response_model=CompetitorRead, status_code=status.HTTP_201_CREATED)
def create_competitor(
    payload: CompetitorCreate,
    db: DbSession,
) -> CompetitorRead:
    """Create a competitor configuration."""
    return CompetitorService(db).create_competitor(payload)


@router.delete("/{competitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_competitor(competitor_id: UUID, db: DbSession) -> None:
    """Delete a competitor configuration."""
    deleted = CompetitorService(db).delete_competitor(competitor_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found")
