---
title: MilmapView Display and Video Recipes
description: Common MilmapView tasks for layer display, camera control, and video layer wiring.
tags:
  - howto
  - milmapview
sources:
  - workflows/wf-api-milmapview.md
---

# MilmapView Display and Video Recipes

## What This Recipe Covers
- Show layers in `NXMilmapView` and control viewpoint.
- Connect composite or video layers when the map view is the primary surface.
- Explain when MilmapView differs from ImageView or PlanetView.
- Explain scale lookup, center movement, cross display, and render-layer ordering.

## Use This Recipe For
- The user asks about 2D map display with tactical overlays.
- The user asks about map-view video layers or view control.
- The user asks how to check whether data exists at a given scale or how to capture the current MilmapView screen.


## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.

## Common Recipes
- `축척 찾기와 이동`
  A common MilmapView explanation uses `SearchScale` or `SearchName`, then `SetGeoToCenter`, then `Zoom` or `ZoomFitRect`.
- `데이터 존재 확인`
  Use `CheckMilmapData` or `IsExistScale` before promising that a scale/area can be shown.
- `레이어 추가와 순서`
  Use `AddRenderLayer`, verify order with `GetLayerOrder`, and apply `ChangeLayerOrder` when the question is about stacking.
- `표시 보조`
  Use `ShowCross`, `RefreshScreen`, and `GetDrawArgs` for cursor/cross/display-state questions.
- `화면 캡처`
  Use `CaptureScreen` when the question is about saving or exporting the current map view.

## Related Pages
- [MilmapView API Workflow](../../workflows/wf-api-milmapview.md)
- [View Screen and World Coordinates](../concepts/view-screen-world-coordinates.md)
- [Provider, Dataset, and Scene Assets](../concepts/provider-dataset-and-scene-assets.md)
