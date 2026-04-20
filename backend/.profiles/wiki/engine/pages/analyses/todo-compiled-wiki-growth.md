---
title: TODO | Compiled Wiki Growth
description: Placeholder analysis page for the gap between current wiki-only answers and future accumulation.
tags:
  - todo
  - analysis
  - llm-wiki
sources:
  - pages/sources/raw-source-root.md
  - pages/topics/todo-raw-source-ingest.md
---

# TODO | Compiled Wiki Growth

## Current Constraint
- The system already uses the wiki as the answer layer.
- It now uses raw sources to rebuild the runtime methods index, but not yet to refresh curated pages and workflows.
- This means the wiki is useful now, but not yet compounding in the `LLM Wiki` sense.

## Practical Implication
- Good answers can already be filed back into the wiki.
- New engine source material reaches the runtime symbol layer automatically, but curated knowledge still requires a future ingest pass.
- Desktop-shell defaults can already be expressed at the workflow layer, with WPF treated as the default unless a workflow or user request says otherwise.

## TODO Questions
- Which source changes should trigger a wiki refresh?
- Which pages should be regenerated versus curated manually?
- What minimum provenance standard should every curated page meet after ingest?
- How should ingest preserve workflow-level desktop-shell defaults such as the current WPF-first rule?
