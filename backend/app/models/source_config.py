"""Source configuration persistence model."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SourceConfig(Base):
    """A persistent source configuration for recurring collection."""

    __tablename__ = "source_configs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    competitor_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("competitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    crawler: Mapped[str] = mapped_column(String(20), nullable=False)
    interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=1440)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    competitor = relationship("Competitor")

