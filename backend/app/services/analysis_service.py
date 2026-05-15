"""Business service for competitive analysis workflows."""

from collections.abc import Callable
from uuid import UUID

from langchain_core.language_models.chat_models import BaseChatModel
from sqlalchemy.orm import Session

from app.agents.workflow import AnalysisWorkflow, ChatInvoker
from app.ai.deepseek import create_deepseek_chat_model
from app.core.config import Settings, settings
from app.models.analysis_report import AnalysisReport
from app.rag.exceptions import RagConfigurationError
from app.schemas.analysis_report import AnalysisReportCreate
from app.services.competitor_service import CompetitorService
from app.services.rag_service import RagService
from app.services.report_service import ReportService

AnalysisEventHandler = Callable[[str, dict[str, object]], None]


class AnalysisService:
    """Coordinate retrieval, agent analysis, and report persistence."""

    def __init__(
        self,
        db: Session,
        app_settings: Settings = settings,
        chat_model: BaseChatModel | ChatInvoker | None = None,
        rag_service: RagService | None = None,
    ) -> None:
        """Initialize analysis dependencies."""
        self.db = db
        self.settings = app_settings
        self.chat_model = chat_model
        self.rag_service = rag_service or RagService(db=db, app_settings=app_settings)
        self.competitor_service = CompetitorService(db)
        self.report_service = ReportService(db)

    def analyze_competitor(
        self,
        competitor_id: UUID,
        query: str,
        context_limit: int,
        event_handler: AnalysisEventHandler | None = None,
    ) -> list[AnalysisReport]:
        """Run competitive analysis and persist reports."""
        competitor = self.competitor_service.get_competitor(competitor_id)
        if competitor is None:
            raise ValueError(f"Competitor not found: {competitor_id}")

        self._emit(event_handler, "retrieving", {"message": "retrieving indexed context"})
        retrieved_context = self.rag_service.search(
            query=query,
            competitor_id=competitor_id,
            limit=context_limit,
        )
        if not retrieved_context:
            raise ValueError("No indexed RAG context found for competitor")
        self._emit(
            event_handler,
            "retrieved",
            {"context_count": len(retrieved_context), "competitor": competitor.name},
        )

        context = "\n\n".join(
            f"Source {index + 1}: {result.text}\nMetadata: {result.metadata}"
            for index, result in enumerate(retrieved_context)
        )
        workflow = AnalysisWorkflow(
            self.chat_model or self._chat_model(),
            event_handler=event_handler,
        )
        outputs = workflow.run(competitor=competitor.name, context=context)
        self._emit(event_handler, "persisting", {"report_count": len(outputs)})
        source_article_ids = sorted(
            {
                result.metadata["article_id"]
                for result in retrieved_context
                if "article_id" in result.metadata
            }
        )

        reports = [
            self.report_service.create_report(
                AnalysisReportCreate(
                    competitor_id=competitor_id,
                    competitor=output.competitor,
                    dimension=output.dimension,
                    risk_level=output.risk_level,
                    summary=output.summary,
                    opportunity_points=output.opportunity_points,
                    threat_points=output.threat_points,
                    confidence_score=output.confidence_score,
                    source_article_ids=source_article_ids,
                )
            )
            for output in outputs
        ]
        self._emit(event_handler, "persisted", {"report_count": len(reports)})
        return reports

    def _chat_model(self) -> BaseChatModel:
        """Create the configured DeepSeek chat model."""
        try:
            return create_deepseek_chat_model(self.settings)
        except RagConfigurationError:
            raise

    def _emit(
        self,
        event_handler: AnalysisEventHandler | None,
        event: str,
        data: dict[str, object],
    ) -> None:
        """Emit one analysis event when a handler is configured."""
        if event_handler is not None:
            event_handler(event, data)
