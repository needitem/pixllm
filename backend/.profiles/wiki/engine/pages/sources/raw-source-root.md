---
title: Raw Source Root
description: Canonical immutable raw source tree used for runtime symbol ingest and future curated ingest work.
tags:
  - source
  - raw
  - todo
---

# Raw Source Root

## Current Role
- Canonical raw source tree: `D:/Pixoneer_Source/PIX_RAG_Source/backend/.profiles/wiki/raw_source/source`
- This path is the immutable source-of-truth root for automatic symbol ingest and future curated accumulation work.
- Current answers must not read this tree directly. For now, responses are grounded only in the `engine` wiki.
- Desktop-shell policy is also defined in the `engine` wiki, where workflow pages currently default desktop samples to WPF unless the user explicitly asks for another stack.
- `engine/.runtime/methods_index.json` is now generated from this tree during wiki rebuild.

## Why This Exists
- It fixes the location of the raw engine codebase for the runtime ingest pipeline.
- It lets the wiki name the source-of-truth explicitly instead of leaving the path implicit.
- It gives TODO pages a concrete location to refer to for the remaining curated ingest work.

## TODO
- Define what counts as ingestable source versus noise (`.vs`, build outputs, generated files).
- Define per-module source manifests or source summaries.
- Extend ingest beyond symbol extraction so raw source changes also update curated wiki pages.
