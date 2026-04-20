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

## Covers
- Host `NXImageView` in WPF through `WindowsFormsHost` when shell context matters.
- Attach raster-backed layers with `AddImageLayer`, then call `ZoomFit` or `ZoomOneToOne`.
- Use `NXImageLayerComposites.GetXDMCompManager` when the question is really about XDM composite display.
- Use `ScreenToWorld` and `WorldToScreen` for cursor-coordinate explanations.

## Reach For This Page When
- The user asks how to show GeoTiff or XDM data in `ImageView`.
- The user asks about adding or removing layers.
- The user asks about background maps, zoom, or pixel reads from a displayed raster.

## Related Pages
- [ImageView API Workflow](../../workflows/wf-api-imageview.md)
- [Raster and XDM API Workflow](../../workflows/wf-api-raster.md)
- [Layer, Composite, and Display Pipeline](../concepts/layer-composite-display-pipeline.md)
- [View Screen and World Coordinates](../concepts/view-screen-world-coordinates.md)
