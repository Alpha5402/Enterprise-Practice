"""Competitive analysis API endpoints."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.rag.exceptions import RagConfigurationError
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analyze")
DbSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest, db: DbSession) -> AnalyzeResponse:
    """Run DeepSeek-powered competitive analysis for one competitor."""
    try:
        reports = AnalysisService(db).analyze_competitor(
            competitor_id=payload.competitor_id,
            query=payload.query,
            context_limit=payload.context_limit,
        )
    except RagConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        message = str(exc)
        error_status = (
            status.HTTP_404_NOT_FOUND
            if message.startswith("Competitor not found")
            else status.HTTP_409_CONFLICT
        )
        raise HTTPException(status_code=error_status, detail=message) from exc
    return AnalyzeResponse(reports=reports)


@router.get("/stream")
def analyze_stream(
    db: DbSession,
    competitor_id: str,
    query: str = "latest competitive signals",
    context_limit: int = 5,
) -> StreamingResponse:
    """Stream analysis progress with server-sent events."""

    def event_stream() -> object:
        yield _sse("started", {"message": "analysis started"})
        try:
            payload = AnalyzeRequest(
                competitor_id=competitor_id,
                query=query,
                context_limit=context_limit,
            )
            yield _sse("retrieving", {"message": "retrieving indexed context"})
            reports = AnalysisService(db).analyze_competitor(
                competitor_id=payload.competitor_id,
                query=payload.query,
                context_limit=payload.context_limit,
            )
            yield _sse("completed", {"reports": [report.id for report in reports]})
        except Exception as exc:
            yield _sse("error", {"message": str(exc)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _sse(event: str, data: dict[str, object]) -> str:
    """Format one server-sent event."""
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"
