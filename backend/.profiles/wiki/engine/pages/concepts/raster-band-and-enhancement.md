---
title: Raster Band and Enhancement Model
description: Cross-cutting concept page for band access, grayscale/RGB composition, and display enhancement.
tags:
  - concept
  - raster
sources:
  - workflows/wf-api-raster.md
---

# Raster Band and Enhancement Model

- `XDMBand` is the unit of raster-band processing.
- In the current wiki routing, grayscale versus RGB display is treated as a composite-assembly question, not a view question.
- Histogram matching, sharpening, and noise interpolation are documented as advanced raster operations separate from simple load/display flows.

## Answering Guidance
- Use this page to explain the shared idea or family boundary first.
- Route back to the owning workflow for exact API names, signatures, and code-level steps.
- Do not rely on this page alone when the answer needs executable call shapes.
