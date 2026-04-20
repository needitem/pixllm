---
title: TODO | Raw Source Ingest
description: Remaining work for extending raw-source ingest beyond the runtime methods index.
tags:
  - todo
  - topic
  - ingest
sources:
  - pages/sources/raw-source-root.md
---

# TODO | Raw Source Ingest

## Current State
- Raw source root is fixed at `D:/Pixoneer_Source/PIX_RAG_Source/backend/.profiles/wiki/raw_source/source`.
- The current system answers from the `engine` wiki only.
- There is now an active ingest pass that reads raw sources and rebuilds `.runtime/methods_index.json` automatically.
- Curated pages and workflows are still maintained separately and are not regenerated from raw sources yet.

## Desired End State
- New or changed raw sources produce updates to:
  - `pages/sources/*`
  - `pages/topics/*`
  - `pages/entities/*`
  - `workflows/*`
  - `.runtime/methods_index.json` when reference extraction changes
- The wiki becomes a compiled, persistent artifact rather than a hand-maintained reference layer.
- Workflow-side desktop-shell defaults, including the current WPF-first rule, survive regeneration instead of being lost during ingest.

## TODO Checklist
- Define source filtering rules.
- Define ingest cadence and trigger conditions.
- Define how contradictions and superseded claims are logged.
- Define which curated page families should be updated per ingest.
