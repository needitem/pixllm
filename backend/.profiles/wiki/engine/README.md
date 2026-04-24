# LLM Wiki

This engine wiki is the persistent compiled knowledge layer for PIXLLM.

## Coordination Facts
```yaml
page_family: coordination_readme
role: wiki_overview
verification_rules:
  - start_here_for_wiki_scope_and_operating_model
  - prefer_workflows_for_usage_questions
  - prefer_methods_for_exact_call_shapes
```

## Layers
- `backend/.profiles/wiki/raw_source/source` is the canonical immutable raw source tree for runtime methods ingest and future curated ingest work.
- Current answers must be grounded from the `engine` wiki only. The raw source tree is not queried directly yet.
- `.runtime/methods_index.json` holds the generated symbol verification index with declaration and implementation anchors.
- `workflows/wf-api-*.md` hold canonical API-family workflows with source-backed `required_symbols` for signature-sensitive answers.
- `pages/howtos/` holds user-task recipes that capture common "how do I do X" questions.
- `pages/concepts/` holds reusable concept pages that explain cross-cutting ideas such as screen/world transforms, layer/composite pipelines, and provider/dataset boundaries.
- `pages/` holds coordination pages plus the curated how-to and concept layers.
- `.runtime/methods_index.json` is the generated method verification catalog for runtime lookup.
- Desktop UI workflows are explanation-first. If a page declares `workflow_bound_to_host_context`, assume WPF only as host context unless the user explicitly asks for another UI stack.

## Current Mode
- Mode: `wiki-only answers`
- Canonical wiki id: `engine`
- Future accumulation root: `D:/Pixoneer_Source/PIX_RAG_Source/backend/.profiles/wiki/raw_source/source`
- Future accumulation work is tracked as TODO pages inside the wiki until ingest is implemented.

## Operating Model
- Prefer API-family workflow pages first when answering usage and implementation questions.
- Treat API-family workflows as hub pages. A good answer should usually read the workflow plus its related how-to, concept, and source pages rather than relying on the workflow alone.
- Use workflow `required_symbols` and the runtime methods index to constrain overloads, enum literals, and `ref/out` directions.
- Use methods pages to verify exact symbol existence, call shape, and source anchors.
- When a stable answer captures a reusable task pattern, prefer filing it back into `pages/howtos/` or `pages/analyses/` so the wiki compounds over time.
- Do not read directly from `raw_source/source` when answering. If the answer is missing from the wiki, leave the ingest gap visible in TODO pages instead of silently switching to raw code.
- Keep duplicated sample/index pages out of the canonical runtime wiki unless they add unique answer constraints.
- For `workflow_bound_to_host_context`, assume the surrounding desktop shell is WPF unless the user explicitly requests another UI stack.

