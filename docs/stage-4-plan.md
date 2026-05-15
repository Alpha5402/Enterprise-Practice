# Stage 4 Plan

## Completed In This Stage

- Created modular prompt files under `backend/app/prompts/`.
- Added strict structured output schema for analysis agents.
- Implemented LangGraph workflow with:
  - `sentiment_agent`
  - `price_agent`
  - `product_agent`
  - `summary_agent`
- Added `AnalysisService` to retrieve RAG context, run agents, and persist reports.
- Added `POST /api/v1/analyze`.
- Added tests for workflow output, report persistence, and API error behavior.

## How It Works

1. The caller sends `competitor_id`, `query`, and `context_limit`.
2. The backend retrieves indexed RAG chunks for the competitor.
3. The LangGraph workflow runs sentiment, price, and product agents.
4. The summary agent synthesizes dimension outputs.
5. Four structured reports are saved to `analysis_reports`.

## Deferred By Design

- SSE streaming is not implemented yet.
- Frontend report detail and settings pages are not implemented yet.
- Automatic scheduled end-to-end collection and analysis remains future work.

## Next Stage

- Add SSE analysis progress streaming.
- Build frontend report list/detail views.
- Add crawler trigger APIs and source configuration.
- Add scheduled daily report generation.

