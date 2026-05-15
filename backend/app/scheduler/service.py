"""APScheduler integration for periodic collection jobs."""

from collections.abc import Callable
from uuid import UUID

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.crawlers.rss.rss_crawler import RssCrawler
from app.db.session import SessionLocal
from app.services.collection_service import CollectionService

SessionFactory = Callable[[], Session]


class SchedulerService:
    """Manage background jobs for collection and future analysis workflows."""

    def __init__(
        self,
        scheduler: BackgroundScheduler | None = None,
        session_factory: SessionFactory = SessionLocal,
    ) -> None:
        """Initialize scheduler dependencies."""
        self.scheduler = scheduler or BackgroundScheduler(timezone="UTC")
        self.session_factory = session_factory

    def schedule_rss_collection(
        self,
        competitor_id: UUID,
        feed_url: str,
        interval_minutes: int,
    ) -> None:
        """Schedule recurring RSS collection for a competitor."""
        self.scheduler.add_job(
            self._collect_rss,
            trigger="interval",
            minutes=interval_minutes,
            args=[competitor_id, feed_url],
            id=f"rss:{competitor_id}:{feed_url}",
            replace_existing=True,
        )

    def start(self) -> None:
        """Start the background scheduler when it is not already running."""
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        """Stop the background scheduler when running."""
        if self.scheduler.running:
            self.scheduler.shutdown()

    def _collect_rss(self, competitor_id: UUID, feed_url: str) -> None:
        """Collect one RSS feed execution and persist articles."""
        db = self.session_factory()
        try:
            CollectionService(db).collect_for_competitor(
                competitor_id=competitor_id,
                source_url=feed_url,
                crawler=RssCrawler(),
            )
        finally:
            db.close()

