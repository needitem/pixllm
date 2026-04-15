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
- `workflows/wf-*.md` hold canonical atomic workflows with source-backed `required_facts` blocks for signature-sensitive answers.
- `workflows/imageview-xdm-display-workflow.md` and `workflows/nximageview-wpf-hosting.md` remain as high-signal scenario workflows.
- `pages/` holds human-oriented coordination pages.
- `01-method-wiki-index.md` is the generated method catalog.

## Operating Model
- Prefer workflow pages first when answering usage and implementation questions.
- Use workflow `required_facts` to constrain overloads, enum literals, and `ref/out` directions.
- Use methods pages to verify exact symbol existence, call shape, and source anchors.
- Keep duplicated sample/index pages out of the canonical runtime wiki unless they add unique answer constraints.
