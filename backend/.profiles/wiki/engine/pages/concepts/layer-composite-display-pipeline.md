---
title: Layer, Composite, and Display Pipeline
description: Cross-cutting concept page for how loaded data becomes one or more visible layers.
tags:
  - concept
  - display
sources:
  - workflows/wf-api-imageview.md
  - workflows/wf-api-raster.md
---

# Layer, Composite, and Display Pipeline

- `XRasterIO` and `XRSLoadFile` answer how files and bands are obtained.
- `XDMComposite` and `XDMCompManager` answer how bands become a displayable composite.
- `NXImageLayerComposites` and related layer types answer how composites reach a view.
- `NXImageView`, `NXMilmapView`, and `NXPlanetView` answer how the user sees and navigates the result.

## Answering Guidance
- Use this page to explain the shared idea or family boundary first.
- Route back to the owning workflow for exact API names, signatures, and code-level steps.
- Do not rely on this page alone when the answer needs executable call shapes.
