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
- When an answer needs a desktop application shell and the user did not ask for another stack, the default shell is WPF.

## Reason
- The current goal is reliable wiki-based answers first.
- Raw-source symbol ingest is active, while broader curated ingest remains future work and is tracked as TODO pages.
- API-family workflows now act as answer hubs and should usually be read together with related how-to, concept, and source-summary pages.

## Consequence
- If the wiki does not contain enough information, the system should expose that gap instead of silently grounding on raw source code.
- The wiki remains the explicit answer boundary until curated ingest is implemented.
- The runtime methods index stays verification-only; workflow pages remain the authority for WPF-vs-host integration guidance.
