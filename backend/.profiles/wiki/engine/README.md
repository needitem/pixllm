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
- `methods/` holds generated API reference pages with declaration and implementation anchors.
- `workflows/` holds answer-routing, scenario, and sample workflows.
- `pages/` holds human-oriented home and future curated synthesis pages.
- `01-method-wiki-index.md` is the generated method catalog.

## Operating Model
- Prefer workflow pages first when answering usage and implementation questions.
- Use methods pages to verify exact symbol existence, call shape, and source anchors.
- File useful analyses back into curated pages instead of leaving them only in chat history.
