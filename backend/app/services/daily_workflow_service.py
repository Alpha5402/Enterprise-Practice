"""Daily collection, indexing, and analysis workflow service."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.crawlers.rss.rss_crawler import RssCrawler
from app.crawlers.web.web_crawler import WebCrawler
from app.schemas.daily_workflow import DailyWorkflowResponse
from app.services.analysis_service import AnalysisService
from app.services.collection_service import CollectionService
from app.services.rag_service import RagService
from app.services.source_config_service import SourceConfigService


class DailyWorkflowService:
    """Run the saved-source daily intelligence workflow."""

    def __init__(self, db: Session) -> None:
        """Initialize workflow dependencies."""
        self.db = db
        self.source_service = SourceConfigService(db)

    def run(self, competitor_id: UUID | None = None) -> DailyWorkflowResponse:
        """Collect, index, and analyze all enabled saved sources."""
        collected_count = 0
        indexed_count = 0
        report_count = 0
        errors: list[str] = []
        sources = [
            source
            for source in self.source_service.list_sources(competitor_id=competitor_id)
            if source.enabled
        ]
        competitor_ids = {source.competitor_id for source in sources}

        for source in sources:
            crawler = RssCrawler() if source.crawler == "rss" else WebCrawler()
            try:
                articles = CollectionService(self.db).collect_for_competitor(
                    competitor_id=source.competitor_id,
                    source_url=source.source_url,
                    crawler=crawler,
                )
                collected_count += len(articles)
            except Exception as exc:
                errors.append(f"{source.name}: collection failed: {exc}")

        for current_competitor_id in competitor_ids:
            try:
                metadata = RagService(self.db).index_competitor_articles(current_competitor_id)
                indexed_count += len(metadata)
            except Exception as exc:
                errors.append(f"{current_competitor_id}: indexing failed: {exc}")
                continue
            try:
                reports = AnalysisService(self.db).analyze_competitor(
                    competitor_id=current_competitor_id,
                    query="每日竞品动态",
                    context_limit=8,
                )
                report_count += len(reports)
            except Exception as exc:
                errors.append(f"{current_competitor_id}: analysis failed: {exc}")

        return DailyWorkflowResponse(
            collected_count=collected_count,
            indexed_count=indexed_count,
            report_count=report_count,
            errors=errors,
        )

