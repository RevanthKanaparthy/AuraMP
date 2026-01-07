# Aura Project Overview

## Purpose
Aura is a research-assistant application that indexes uploaded academic materials and answers queries using a local LLM. It focuses on returning answers strictly from the user-provided context.

## Architecture
- Backend: FastAPI with endpoints for upload, retrieval (RAG), authentication, and Q&A generation.
- Frontend: React (Vite + Tailwind) single-page app in `aura-frontend/`.
- LLM: Local Ollama (default) for generation.
- Retrieval: Optional embeddings via ChromaDB; advanced re-ranking/compression when enabled.
- Database: Async PostgreSQL via psycopg (graceful fallback if offline).

## Key Features
- Document ingestion and chunking
- Health endpoint for LLM and DB status
- Retrieval-augmented generation with advanced/context-optimized flow when available
- Secure JWT-based authentication

## Run Backend
- Fast start:
  - `python run_backend.py`
- Manual:
  - Set `LLM_PROVIDER=ollama` and `SKIP_EMBEDDINGS=1` for development
  - `python -m uvicorn backend_complete:app --reload --host 0.0.0.0 --port 8000`
  - Health: `GET http://localhost:8000/health`

## Run Frontend
- `cd aura-frontend`
- `npm install`
- `npm run dev`

## Configuration
- Environment variables:
  - `LLM_PROVIDER` (default `ollama`)
  - `SKIP_EMBEDDINGS` (set `1` to skip embeddings init)
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
  - `SECRET_KEY` (change from default)

