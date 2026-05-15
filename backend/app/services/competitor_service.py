"""Business operations for competitor management."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.competitor import Competitor
from app.schemas.competitor import CompetitorCreate


class CompetitorService:
    """Coordinate persistence operations for competitors."""

    def __init__(self, db: Session) -> None:
        """Initialize the service with a database session."""
        self.db = db

    def list_competitors(self) -> list[Competitor]:
        """Return all competitors ordered by creation time."""
        statement = select(Competitor).order_by(Competitor.created_at.desc())
        return list(self.db.scalars(statement).all())

    def create_competitor(self, payload: CompetitorCreate) -> Competitor:
        """Create and persist a competitor."""
        competitor = Competitor(**payload.model_dump())
        self.db.add(competitor)
        self.db.commit()
        self.db.refresh(competitor)
        return competitor

    def delete_competitor(self, competitor_id: UUID) -> bool:
        """Delete a competitor by id and report whether it existed."""
        competitor = self.db.get(Competitor, competitor_id)
        if competitor is None:
            return False
        self.db.delete(competitor)
        self.db.commit()
        return True

