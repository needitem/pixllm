# Engine Wiki Home

## Coordination Facts
```yaml
page_family: coordination_home
role: human_landing_page
verification_rules:
  - point_users_to_index_workflows_and_runtime_methods_index
  - keep_this_page_high_level_and_human_oriented
```

## Purpose
- Use this wiki as the persistent answer and verification layer for engine questions.
- Current answer policy is `wiki-only`: answer from pages that already exist in this wiki.
- Treat `D:/Pixoneer_Source/PIX_RAG_Source/backend/.profiles/wiki/raw_source/source` as ingest input and source-of-truth storage, not direct query ground truth.
- Prefer workflow pages for usage and composition questions, but read them as family hubs together with related how-to and concept pages.
- Prefer workflow `required_symbols` plus the runtime methods index when exact signatures matter.
- Prefer `.runtime/methods_index.json` for exact symbol existence, call shape, and source anchors.
- For desktop UI answers, default to WPF unless the user explicitly asks for a different shell.

## Start Here
- [index.md](../index.md)
- [current-answer-policy.md](../pages/decisions/current-answer-policy.md)
- [raw-source-root.md](../pages/sources/raw-source-root.md)
- [todo-raw-source-ingest.md](../pages/topics/todo-raw-source-ingest.md)
- [wf-api-imageview.md](../workflows/wf-api-imageview.md)
- [wf-api-raster.md](../workflows/wf-api-raster.md)
- [wf-api-coordinate.md](../workflows/wf-api-coordinate.md)
- [wf-api-videoview.md](../workflows/wf-api-videoview.md)
- [imageview-display-recipes.md](../pages/howtos/imageview-display-recipes.md)
- [raster-load-and-composite.md](../pages/howtos/raster-load-and-composite.md)
- [layer-composite-display-pipeline.md](../pages/concepts/layer-composite-display-pipeline.md)
- [view-screen-world-coordinates.md](../pages/concepts/view-screen-world-coordinates.md)
- Runtime method verification lives in `.runtime/methods_index.json`.
