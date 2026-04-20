---
title: Core Utils File and System Recipes
description: Common core-utils tasks for filesystem, string, process, and helper APIs.
tags:
  - howto
  - core-utils
sources:
  - workflows/wf-api-core-utils.md
---

# Core Utils File and System Recipes

## What This Recipe Covers
- File, path, process, and general helper tasks that do not belong to a view family.
- Validate engine licenses and inspect whether the current license is still valid.
- Switch the engine config path and use progress-reporting helpers such as `XThread.SendMessagePercent`.
- Explain where to stop using core utils and switch to domain APIs.

## Use This Recipe For
- The user asks about general utility APIs rather than display, raster, or coordinate families.


## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.

## Common Recipes
- `현재 라이선스 확인`
  Use `ValidateLicense` for explicit validation requests, and `IsValidLicense` for current status, type, expiry, and path.
- `config path 전환`
  Use `SetConfigPath` when the user is switching engine configuration roots before a later initialization step.
- `percent 진행률 보고`
  Use `SendMessagePercent` for generic long-running task progress instead of confusing it with DFS exporter progress APIs.

## Related Pages
- [Core Utils API Workflow](../../workflows/wf-api-core-utils.md)
- [Engine Core Utility Scope](../concepts/engine-core-utility-scope.md)
