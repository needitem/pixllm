# Engine Wiki Schema

## Coordination Facts
```yaml
page_family: coordination_schema
role: canonical_contract
verification_rules:
  - use_this_page_for_family_and_role_resolution
  - keep_runtime_and_wiki_family_names_in_sync
```

## Families
- `README.md`, `SCHEMA.md`, `index.md`, `log.md`, `pages/home.md`: coordination spine.
- `pages/sources/raw-source-root.md`: canonical raw source root placeholder and ingest boundary.
- `pages/decisions/current-answer-policy.md`: current answer contract for this project.
- `pages/topics/todo-raw-source-ingest.md`, `pages/analyses/todo-compiled-wiki-growth.md`: TODO placeholders for future accumulation work.
- `pages/howtos/*.md`: reusable task-oriented recipe pages derived from repeated user questions.
- `pages/concepts/*.md`: concept pages for cross-cutting explanations that multiple API families reuse.
- `.runtime/methods_index.json`: generated method verification catalog.
- `.runtime/methods_index.json`: generated method verification records with declaration-based anchors.
- `workflows/wf-api-*.md`: canonical API-family workflows with source-backed `required_facts` for answer routing and signature checks.

## Raw Source Root
- Canonical immutable raw source tree: `D:/Pixoneer_Source/PIX_RAG_Source/backend/.profiles/wiki/raw_source/source`
- The raw source tree is the source for runtime methods ingest and remains the source-of-truth for future curated accumulation work.
- Until ingest is implemented, answers must be grounded only in pages that already exist under the `engine` wiki.

## Rules
- Current answer policy is `wiki-only`.
- Do not answer directly from `raw_source/source`.
- Treat `raw_source/source` as immutable source-of-truth storage for runtime ingest and future curated ingest passes.
- Use the TODO placeholder pages to track gaps between the current wiki-only mode and the future compiled-knowledge mode.
- Use API-family workflow pages as the primary answer path for usage questions.
- Treat workflow pages as family hubs, not standalone answers: prefer retrieving the workflow together with its linked `pages/howtos/*`, `pages/concepts/*`, and source pages.
- Add a `## Knowledge Bundle` YAML section to workflow pages when they need stable related-page routing for how-to, concept, dependency-workflow, or source-summary pages.
- Treat workflow `required_facts` as the first signature-level constraint set.
- Prefer one broad API family workflow over many tiny scenario workflows when the same control/type is the primary user-facing surface.
- When a question yields a stable reusable explanation, file it back into `pages/howtos/*` or `pages/analyses/*` instead of leaving it only in chat history.
- Cross-check methods pages before emitting exact call shapes.
- Treat declaration lines as symbol-existence evidence and implementation lines as source anchors.
- Keep sample/index-style workflow pages out of the canonical runtime wiki when they only duplicate routing or sample guidance.
- Do not invent overloads, enum literals, or `ref/out` directions beyond the verified pages.
- Treat `workflow_bound_to_host_context` as a host-context contract: default to WPF only when the explanation needs to mention the surrounding desktop shell.

