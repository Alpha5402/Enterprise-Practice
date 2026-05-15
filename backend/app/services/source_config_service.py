"""Business operations for source configurations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.source_config import SourceConfig
from app.schemas.source_config import SourceConfigCreate


class SourceConfigService:
    """Coordinate persistence for source configurations."""

    def __init__(self, db: Session) -> None:
        """Initialize the service with a database session."""
        self.db = db

    def list_sources(self, competitor_id: UUID | None = None) -> list[SourceConfig]:
        """Return configured sources, optionally scoped to one competitor."""
        statement = select(SourceConfig).order_by(SourceConfig.created_at.desc())
        if competitor_id is not None:
            statement = statement.where(SourceConfig.competitor_id == competitor_id)
        return list(self.db.scalars(statement).all())

    def create_source(self, payload: SourceConfigCreate) -> SourceConfig:
        """Create and persist a source configuration."""
        values = payload.model_dump()
        values["source_url"] = str(payload.source_url)
        source = SourceConfig(**values)
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def get_source(self, source_id: UUID) -> SourceConfig | None:
        """Return a source configuration by id."""
        return self.db.get(SourceConfig, source_id)

    def delete_source(self, source_id: UUID) -> bool:
        """Delete a source configuration by id."""
        source = self.db.get(SourceConfig, source_id)
        if source is None:
            return False
        self.db.delete(source)
        self.db.commit()
        return True
