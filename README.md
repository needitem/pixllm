# PIXLLM Workbench

Desktop workbench and FastAPI backend for grounded code chat, local workspace tracing, and tool-driven retrieval.

## What It Is

PIXLLM Workbench combines an Electron desktop client with a backend service that can:

- run chat and streaming chat APIs
- inspect a local code workspace through tool calls
- blend local evidence with backend retrieval
- manage runs, prompts, conversations, imports, and knowledge resources

The repository is organized around two runtime surfaces:

- [`desktop/`](./desktop): Electron + Svelte desktop app
- [`backend/`](./backend): FastAPI service, retrieval logic, tool runtime, and orchestration

## Repository Layout

- [`desktop/`](./desktop): desktop shell, local agent loop, renderer UI, packaging
- [`backend/`](./backend): API server, chat pipeline, retrieval, storage, Docker stack
- [`docs/`](./docs): design notes and reference material

## Backend

The backend is a FastAPI application that exposes:

- `/api/v1/chat` and `/api/v1/chat/stream`
- auth and health endpoints
- search, models, prompts, conversations, runs, pipelines, tools, and imports

The default deployment path is Docker Compose.

```bash
cd backend
copy .env.compose.example .env
docker compose up -d --build
```

## Desktop

The desktop app packages the local workspace tools and the renderer into a portable Electron build.

```bash
cd desktop
npm install
npm run build
npm run dist:portable
```

For local development:

```bash
cd desktop
npm run dev
```

## Configuration

Main runtime configuration lives in:

- [`backend/.profiles/rag_config.yaml`](./backend/.profiles/rag_config.yaml)
- [`backend/.env.example`](./backend/.env.example)
- [`backend/.env.compose.example`](./backend/.env.compose.example)

## Current Focus

This codebase is tuned for grounded code analysis rather than generic chat. The current implementation emphasizes:

- local workspace evidence first
- bounded tool-driven tracing for code explanation
- backend retrieval only when local evidence is insufficient

## Docs

Reference material remains under [`docs/`](./docs), but this README is intended to be the primary GitHub landing page.
