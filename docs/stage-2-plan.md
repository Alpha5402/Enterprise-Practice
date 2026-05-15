# Stage 2 Plan

## Completed In This Stage

- Added database models for collected articles, analysis reports, and vector metadata.
- Added Alembic migration `202605150002_add_collection_and_reports`.
- Implemented article, report, embedding metadata, and collection services.
- Implemented modular RSS and web crawler adapters.
- Added text cleaning for crawler output.
- Added APScheduler service boundary for recurring RSS collection.
- Added report read APIs.
- Added tests for crawler parsing, text cleaning, and report APIs.

## Deferred By Design

- `POST /analyze` remains deferred until the LangGraph workflow stage.
- RAG chunking, embeddings, and vector store writes remain deferred until the RAG stage.
- Claude-backed structured output remains deferred until Agent Workflow implementation.

## Next Stage

- Implement RAG text chunking.
- Add `VectorStoreService` abstraction.
- Wire Chroma as the first vector store backend.
- Persist embedding metadata when chunks are stored.
- Add retrieval APIs or internal service methods used by the future Agent workflow.

