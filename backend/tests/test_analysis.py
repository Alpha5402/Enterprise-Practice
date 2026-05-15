"""Analysis workflow and API tests."""

from typing import Any

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from sqlalchemy.orm import Session

from app.agents.workflow import AnalysisWorkflow
from app.main import app
from app.models.competitor import Competitor
from app.rag.vector_store import VectorSearchResult
from app.services.analysis_service import AnalysisService


class FakeChatModel:
    """Deterministic chat model for workflow tests."""

    def invoke(self, input: list[Any]) -> AIMessage:
        """Return strict JSON based on the system prompt dimension."""
        system_prompt = input[0].content
        if "sentiment analysis agent" in system_prompt:
            dimension = "sentiment"
        elif "pricing analysis agent" in system_prompt:
            dimension = "price"
        elif "product analysis agent" in system_prompt:
            dimension = "product"
        else:
            dimension = "summary"
        return AIMessage(
            content=(
                '{"competitor":"Acme Cloud",'
                f'"dimension":"{dimension}",'
                '"risk_level":"medium",'
                '"summary":"Structured analysis summary.",'
                '"opportunity_points":["Differentiate positioning"],'
                '"threat_points":["Competitive pressure"],'
                '"confidence_score":0.75}'
            )
        )


class FakeRagService:
    """Deterministic RAG service for analysis tests."""

    def __init__(self, results: list[VectorSearchResult]) -> None:
        """Initialize fake retrieval results."""
        self.results = results

    def search(
        self,
        query: str,
        competitor_id: object | None = None,
        limit: int = 5,
    ) -> list[VectorSearchResult]:
        """Return deterministic retrieval results."""
        _ = (query, competitor_id)
        return self.results[:limit]


def create_competitor(db_session: Session) -> Competitor:
    """Create a competitor for analysis tests."""
    competitor = Competitor(
        name="Acme Cloud",
        industry="Cloud Infrastructure",
        description="Enterprise cloud platform",
        keywords=["pricing"],
        enabled=True,
    )
    db_session.add(competitor)
    db_session.commit()
    db_session.refresh(competitor)
    return competitor


def test_analysis_workflow_returns_all_dimensions() -> None:
    """LangGraph workflow returns strict structured outputs for all agents."""
    outputs = AnalysisWorkflow(FakeChatModel()).run(
        competitor="Acme Cloud",
        context="Acme changed pricing and launched a product.",
    )

    assert [output.dimension for output in outputs] == [
        "sentiment",
        "price",
        "product",
        "summary",
    ]


def test_analysis_service_persists_reports(db_session: Session) -> None:
    """Analysis service persists all workflow outputs as reports."""
    competitor = create_competitor(db_session)
    service = AnalysisService(
        db=db_session,
        chat_model=FakeChatModel(),
        rag_service=FakeRagService(
            [
                VectorSearchResult(
                    id="vector-1",
                    text="Acme reduced entry-tier pricing.",
                    metadata={"article_id": "article-1", "competitor_id": str(competitor.id)},
                    distance=0.1,
                )
            ]
        ),
    )

    reports = service.analyze_competitor(
        competitor_id=competitor.id,
        query="pricing",
        context_limit=5,
    )

    assert len(reports) == 4
    assert {report.dimension for report in reports} == {"sentiment", "price", "product", "summary"}


def test_analysis_service_requires_rag_context(db_session: Session) -> None:
    """Analysis service rejects analysis when no indexed context exists."""
    competitor = create_competitor(db_session)
    service = AnalysisService(
        db=db_session,
        chat_model=FakeChatModel(),
        rag_service=FakeRagService([]),
    )

    try:
        service.analyze_competitor(competitor.id, "pricing", 5)
    except ValueError as exc:
        assert "No indexed RAG context" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_analyze_api_returns_409_without_rag_context(db_session: Session) -> None:
    """Analyze API reports missing RAG context before calling DeepSeek."""
    competitor = create_competitor(db_session)
    client = TestClient(app)

    response = client.post(
        "/api/v1/analyze",
        json={"competitor_id": str(competitor.id), "query": "pricing", "context_limit": 5},
    )

    assert response.status_code in {409, 503}

