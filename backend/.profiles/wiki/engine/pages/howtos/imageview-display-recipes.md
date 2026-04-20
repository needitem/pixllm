---
title: ImageView Display Recipes
description: Common ImageView tasks for loading, attaching layers, fitting view, and reading pixel values.
tags:
  - howto
  - imageview
  - display
sources:
  - workflows/wf-api-imageview.md
  - workflows/wf-api-raster.md
---

# ImageView Display Recipes

## What This Recipe Covers
- Host `NXImageView` in WPF through `WindowsFormsHost` when shell context matters.
- Attach raster-backed layers with `AddImageLayer`, then call `ZoomFit` or `ZoomOneToOne`.
- Use `NXImageLayerComposites.GetXDMCompManager` when the question is really about XDM composite display.
- Use `ScreenToWorld` and `WorldToScreen` for cursor-coordinate explanations.

## Use This Recipe For
- The user asks how to show GeoTiff or XDM data in `ImageView`.
- The user asks about adding or removing layers.
- The user asks about background maps, zoom, or pixel reads from a displayed raster.


## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.

## Common Recipes
- `GeoTiff/XDM 표시`
  A typical answer flow is: load the raster through the Raster workflow, attach the resulting layer with `AddImageLayer`, then explain `ZoomFit` or `ZoomOneToOne`.
- `배경지도 설정`
  Use `SetBackgroundMap`, and mention `RefreshScreen` when the answer needs an explicit redraw step.
- `좌표 변환`
  Use `ScreenToWorld` and `WorldToScreen` together when the answer needs to show both directions.
- `픽셀값 읽기`
  Explain whether the question is about view coordinates or XDM composite pixel reads before pointing to `ReadPixelValues`.
- `comp-link / 비교용 레이어`
  Use `GetXDLCompManager1/2` or `GetXDMCompManager` depending on whether the user means linked display layers or raw XDM composite state.

## Related Pages
- [ImageView API Workflow](../../workflows/wf-api-imageview.md)
- [Raster and XDM API Workflow](../../workflows/wf-api-raster.md)
- [Layer, Composite, and Display Pipeline](../concepts/layer-composite-display-pipeline.md)
- [View Screen and World Coordinates](../concepts/view-screen-world-coordinates.md)
