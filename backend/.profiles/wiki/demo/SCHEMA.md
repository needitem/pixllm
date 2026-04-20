# LLM Wiki Schema

## Canonical Structure

- Raw source root for runtime methods ingest and future curated ingest: `D:/Pixoneer_Source/PIX_RAG_Source/backend/.profiles/wiki/raw_source/source`.
- `README.md`: human-readable overview of the wiki and its operating model.
- `SCHEMA.md`: editing rules and directory conventions.
- `index.md`: generated content-oriented catalog for navigation.
- `log.md`: chronological append-only record of ingest, writeback, and lint events.
- `pages/sources/raw-source-root.md`: canonical raw source root and ingest boundary.
- `pages/decisions/current-answer-policy.md`: current answer contract for this project.
- `pages/topics/todo-raw-source-ingest.md`, `pages/analyses/todo-compiled-wiki-growth.md`: TODO placeholders for future accumulation work.
- `pages/home.md`: curated landing page for high-level orientation.
- `pages/sources/`: source summary pages derived from raw sources.
- `pages/topics/`: curated synthesis pages for recurring themes or features.
- `pages/entities/`: entity-centric reference pages when named subjects matter.
- `pages/analyses/`: saved query answers, comparisons, and deep dives.
- `pages/decisions/`: decision records and notable tradeoffs.
- `workflows/`: verified task or implementation workflows.
- `.runtime/methods_index.json`: generated symbol verification index used by runtime lookup.

## Editing Rules

- Current answer mode is `wiki-only`: answer from pages that already exist in the active wiki.
- Do not read directly from `raw_source/source` when answering questions.
- Treat the raw source root as immutable ingest input and track remaining curated-ingest gaps with TODO pages.
- Prefer updating curated pages under `pages/` and `workflows/` over editing generated runtime indices.
- Every curated page should carry explicit provenance via `sources` frontmatter or inline source anchors.
- `index.md` must be rebuilt after ingest, writeback, or major manual edits.
- `log.md` must record ingest, writeback, lint, and repair events.
- Keep relative markdown links stable.
- If a workflow answer needs a desktop shell and the user did not ask for another stack, default to WPF.