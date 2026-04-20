---
title: Current Answer Policy
description: Current operating contract for engine answers with raw-source symbol ingest enabled and curated ingest still pending.
tags:
  - decision
  - policy
  - wiki-only
sources:
  - README.md
  - SCHEMA.md
  - pages/sources/raw-source-root.md
---

# Current Answer Policy

## Decision
- Engine answers are currently grounded only in the `engine` wiki.
- The raw source tree at `D:/Pixoneer_Source/PIX_RAG_Source/backend/.profiles/wiki/raw_source/source` is not used directly for answer generation.

## Consequence
- If the wiki does not contain enough information, expose the gap instead of silently grounding on raw source code.
- The wiki remains the explicit answer boundary until curated ingest is implemented.