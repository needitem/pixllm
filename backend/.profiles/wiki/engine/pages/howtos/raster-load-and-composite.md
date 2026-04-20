---
title: Raster Load and Composite Recipes
description: Common raster workflows for load, band access, grayscale/RGB display, and enhancement setup.
tags:
  - howto
  - raster
  - xdm
sources:
  - workflows/wf-api-raster.md
  - workflows/wf-api-imageview.md
---

# Raster Load and Composite Recipes

## What This Recipe Covers
- Initialize `XRasterIO`, load files, and inspect subdatasets before selecting bands.
- Use `XRSLoadFile.GetBandAt` to fetch bands for grayscale or RGB composition.
- Assemble `XDMComposite` and register it through `XDMCompManager`.
- Tune cut and stretch before handing the composite to `ImageView`.

## Use This Recipe For
- The user asks how to load GeoTiff, XDM, or raw raster files.
- The user asks how to switch between grayscale and color display.
- The user asks how to improve displayed raster quality.


## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.

## Common Recipes
- `GeoTiff/XDM 로드`
  A typical raster flow is `Initialize`, then `LoadFile`, then inspect subdatasets or fetch bands with `GetBandAt`.
- `raw raster 로드`
  Use `LoadRawFile` only when the question is about explicit raw data parameters rather than normal file formats.
- `흑백/칼라 도시`
  A typical composite explanation chooses bands, then calls `SetBand`, then registers the composite with `AddXDMComposite`.
- `합성 순서 바꾸기`
  Use `MoveComposite` or remove/re-add composites when the question is about stacking or visible ordering.
- `stretch/cut`
  Group `SetCutType`, `SetStretchType`, `SetStretchCoverage`, `SetCutMin`, and `SetCutMax` into one explanation instead of listing them separately.

## Related Pages
- [Raster and XDM API Workflow](../../workflows/wf-api-raster.md)
- [ImageView API Workflow](../../workflows/wf-api-imageview.md)
- [Raster Band and Enhancement Model](../concepts/raster-band-and-enhancement.md)
