# LLM Wiki

This wiki compiles knowledge for `demo` into persistent markdown pages.

## Layers

- Canonical raw source root for runtime methods ingest and future curated ingest: `D:/Pixoneer_Source/PIX_RAG_Source/backend/.profiles/wiki/raw_source/source`.
- Current answer mode is wiki-only: answer from pages already compiled into this wiki.
- `raw/` keeps immutable source manifests and ingestion traces once ingest exists.
- `pages/` keeps curated synthesis pages for topics, entities, analyses, and decisions.
- Structured symbol verification lives in `.runtime/methods_index.json`.
- `workflows/` keep verified task and implementation guidance.
- When a workflow explanation needs to mention a desktop shell and none is specified, default to WPF.

## Operations

- Runtime methods ingest is active: raw sources are compiled into `.runtime/methods_index.json` during rebuild.
- Query should use the wiki first and stay within curated wiki pages, using the runtime methods index only for symbol verification.
- Lint should detect broken links, orphan pages, and uncited curated claims.