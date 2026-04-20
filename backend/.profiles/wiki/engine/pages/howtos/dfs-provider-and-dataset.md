---
title: DFS Provider and Dataset Recipes
description: Common DFS tasks for provider setup, dataset registration, and lookup.
tags:
  - howto
  - dfs
sources:
  - workflows/wf-api-dfs.md
  - workflows/wf-api-planetview.md
---

# DFS Provider and Dataset Recipes

## What This Recipe Covers
- Configure or inspect DFS providers and dataset registrations.
- Explain when a question is about provider lookup rather than view rendering.
- Build provider groups and run PBI/PBE export while tracking progress.

## Use This Recipe For
- The user asks how a dataset is registered, found, or grouped.
- The user asks DFS questions that later feed PlanetView or map views.
- The user asks about export progress, cancel, or how `XDMCompManager` enters a provider group.


## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.

## Common Recipes
- `provider group 준비`
  A typical provider-group setup uses `XPBIProviderGroup.AddPBIFile`, `AddXDMCompManager`, and `AddXNS` before export.
- `PBI export 실행`
  A common PBI export explanation uses `XPBIProviderExporter.SetSource` when needed, then `Export2PBI`, and polls `GetPercent` during long-running jobs.
- `PBE export 실행`
  A common PBE export explanation uses `XPBEProviderExporter.SetSource`, `Export2PBE`, and `GetPercent` in the same control pattern.
- `export 중단`
  Use `Cancel` on the matching exporter rather than clearing provider inputs mid-run.

## Related Pages
- [DFS API Workflow](../../workflows/wf-api-dfs.md)
- [PlanetView API Workflow](../../workflows/wf-api-planetview.md)
- [Provider, Dataset, and Scene Assets](../concepts/provider-dataset-and-scene-assets.md)
