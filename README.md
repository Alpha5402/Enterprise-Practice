# Competitive Intelligence System

Enterprise-grade competitive dynamics tracking and benchmark analysis system based on Claude, LangChain, LangGraph, FastAPI, and React.

## Stage 1 Scope

- Docker Compose runtime for backend, frontend, PostgreSQL, Redis, and ChromaDB.
- FastAPI backend with versioned API routing.
- SQLAlchemy model and Alembic migration for competitor management.
- Competitor CRUD API for listing, creating, and deleting competitors.
- React, TypeScript, Vite, TailwindCSS, shadcn/ui-compatible foundation.
- API-backed dashboard with competitor management and empty states for future reports.

## Local Development

```bash
cp .env.example .env
docker compose up --build
```

Backend docs are available at `http://localhost:8000/docs`.
Frontend is available at `http://localhost:5173`.

