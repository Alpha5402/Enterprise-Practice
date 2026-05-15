# Competitive Intelligence System

Enterprise-grade competitive dynamics tracking and benchmark analysis system based on Claude, LangChain, LangGraph, FastAPI, and React.

## Stage 1 Scope

- Docker Compose runtime for backend, frontend, PostgreSQL, Redis, and ChromaDB.
- FastAPI backend with versioned API routing.
- SQLAlchemy model and Alembic migration for competitor management.
- Competitor CRUD API for listing, creating, and deleting competitors.
- React, TypeScript, Vite, TailwindCSS, shadcn/ui-compatible foundation.
- API-backed dashboard with competitor management and empty states for future reports.

## Stage 2 Scope

- SQLAlchemy models and Alembic migration for `news_articles`, `analysis_reports`, and `embeddings_metadata`.
- Modular RSS and webpage crawlers with normalized article output.
- Text cleaning service for crawler output.
- APScheduler service boundary for recurring RSS collection jobs.
- Report read APIs: `GET /api/v1/reports` and `GET /api/v1/reports/{id}`.

## Stage 3 Scope

- Text chunking for collected article content.
- LangChain-compatible local embedding provider for RAG indexing.
- `VectorStoreService` abstraction with ChromaDB implementation.
- RAG indexing service that stores chunks in Chroma and records `embeddings_metadata`.
- RAG retrieval API for semantically searching indexed chunks.

## Stage 4 Scope

- Prompt files for sentiment, price, product, and summary agents.
- LangGraph workflow that runs dimension agents and produces a summary report.
- DeepSeek chat model integration through LangChain.
- Strict Pydantic JSON parsing for agent outputs.
- Analysis API: `POST /api/v1/analyze`.

## Stage 5 Scope

- Collection API: `POST /api/v1/collect`.
- Article list API: `GET /api/v1/articles`.
- Competitor batch indexing API: `POST /api/v1/competitors/{id}/index`.
- Frontend operations dashboard for collect, index, analyze, and report review.

## Local Development

```bash
cp .env.example .env
docker compose up --build
```

The backend container runs `alembic upgrade head` before starting FastAPI, so a fresh PostgreSQL volume is migrated automatically.

Backend docs are available at `http://localhost:8000/docs`.
Frontend is available at `http://localhost:5173`.

DeepSeek model calls require `DEEPSEEK_API_KEY` in `.env`. RAG indexing uses a LangChain-compatible local embedding adapter backed by Chroma's default embedding function.

Basic workflow:

1. Create a competitor.
2. Select the competitor in the dashboard.
3. Collect from an RSS or web URL.
4. Index collected articles.
5. Run analysis and review generated reports.


## Quality Checks

```bash
scripts/check.sh
```
