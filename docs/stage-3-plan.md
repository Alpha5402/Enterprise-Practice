# Stage 3 Plan

## Completed In This Stage

- Added configurable RAG chunk size, overlap, collection name, embedding model, and DeepSeek settings.
- Implemented source text chunking with stable offsets.
- Added a LangChain-compatible local embedding adapter backed by Chroma's default embedding function.
- Added a vector store protocol and ChromaDB implementation.
- Implemented `RagService` for article indexing and semantic retrieval.
- Persisted vector metadata through `embeddings_metadata`.
- Added RAG APIs:
  - `POST /api/v1/rag/articles/index`
  - `POST /api/v1/rag/search`
- Added tests for chunking, embedding configuration, indexing, retrieval filtering, and API failure behavior.

## Deferred By Design

- LangGraph agent workflow remains deferred until the next stage.
- Claude structured output remains deferred until the Agent stage.
- DeepSeek is configured as the LLM path for the future Agent stage through LangChain.

## Next Stage

- Create prompt files under `backend/app/prompts/`.
- Implement LangGraph nodes for sentiment, price, product, and summary analysis.
- Add strict Pydantic structured output for analysis reports.
- Implement `POST /api/v1/analyze`.
- Add SSE streaming for analysis progress.
