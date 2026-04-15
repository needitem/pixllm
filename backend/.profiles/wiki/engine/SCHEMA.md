# Engine Wiki Schema

## Families
- `README.md`, `SCHEMA.md`, `index.md`, `log.md`, `pages/home.md`: coordination spine.
- `01-method-wiki-index.md`: generated method catalog.
- `methods/*.md`: generated method reference pages.
- `workflows/wf-*.md`: normalized atomic workflows used for routing and answer synthesis.
- retained curated workflow/example pages in `workflows/`: richer scenario references and sample indexes.

## Rules
- Use workflow pages as the primary answer path for usage questions.
- Cross-check methods pages before emitting exact call shapes.
- Treat declaration lines as symbol-existence evidence and implementation lines as source anchors.
- Do not invent overloads, enum literals, or `ref/out` directions beyond the verified pages.
