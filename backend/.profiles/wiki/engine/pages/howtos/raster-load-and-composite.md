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

## Covers
- Initialize `XRasterIO`, load files, and inspect subdatasets before selecting bands.
- Use `XRSLoadFile.GetBandAt` to fetch bands for grayscale or RGB composition.
- Assemble `XDMComposite` and register it through `XDMCompManager`.
- Tune cut and stretch before handing the composite to `ImageView`.

## Reach For This Page When
- The user asks how to load GeoTiff, XDM, or raw raster files.
- The user asks how to switch between grayscale and color display.
- The user asks how to improve displayed raster quality.

## Related Pages
- [Raster and XDM API Workflow](../../workflows/wf-api-raster.md)
- [ImageView API Workflow](../../workflows/wf-api-imageview.md)
- [Raster Band and Enhancement Model](../concepts/raster-band-and-enhancement.md)
