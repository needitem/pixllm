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

## TODO Checklist
- Define source filtering rules.
- Define ingest cadence and trigger conditions.
- Define contradiction/supersession recording.
- Define which curated page families update per ingest.