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
- `01-method-wiki-index.md`: generated method catalog.
- `methods/*.md`: generated method reference pages with declaration-based verification anchors.
- `workflows/wf-*.md`: canonical atomic workflows with source-backed `required_facts` for answer routing and signature checks.
- `workflows/imageview-xdm-display-workflow.md`, `workflows/nximageview-wpf-hosting.md`: retained high-signal scenario workflows.

## Rules
- Use workflow pages as the primary answer path for usage questions.
- Treat workflow `required_facts` as the first signature-level constraint set.
- Cross-check methods pages before emitting exact call shapes.
- Treat declaration lines as symbol-existence evidence and implementation lines as source anchors.
- Keep sample/index-style workflow pages out of the canonical runtime wiki when they only duplicate routing or sample guidance.
- Do not invent overloads, enum literals, or `ref/out` directions beyond the verified pages.
