---
title: Vector Load and Overlay Recipes
description: Common vector tasks for loading, styling, and overlaying vector content on views.
tags:
  - howto
  - vector
sources:
  - workflows/wf-api-vector.md
  - workflows/wf-api-coordinate.md
---

# Vector Load and Overlay Recipes

## What This Recipe Covers
- Load vector content and inspect basic geometry or bounds.
- Attach vector overlays to the appropriate display surface.
- Explain where vector questions end and coordinate-transform questions begin.

## Use This Recipe For
- The user asks how to load shapefile-like data or vector overlays.
- The user asks about vector object coordinates, bounds, or rendering on top of imagery.

## Minimal C# Flow
Use this shape when the user asks how to load an SHP/vector file and overlay it on `NXImageView`.
Include `Pixoneer.NXDL.NCC` when the sample declares `XSpatialReference`.
The `pInSR` argument is by-ref, so pass a local `XSpatialReference` with `ref`; do not pass `null` directly.

```csharp
XVectorIO vectorIO = new XVectorIO();
string error = "";
if (!vectorIO.Initialize(out error))
    return;

XSpatialReference srIn = new XSpatialReference();
srIn.importFromEPSG(epsgCode);

XvcBase vectorBase = vectorIO.LoadFile(shpPath, out error, ref srIn);
if (vectorBase == null)
    return;

NXImageLayerVectorDisplay vectorLayer = new NXImageLayerVectorDisplay();
vectorLayer.SetDataSource(vectorBase);
vectorLayer.SetUpdateNeeded();

NXImageLayer imageLayer = vectorLayer as NXImageLayer;
imageView.AddImageLayer(ref imageLayer);
imageView.ZoomFit();
imageView.RefreshScreen();
```

Use `AddDataSource` instead of `SetDataSource` when the layer should keep existing vector sources and append another `XvcBase`.
Call `SetUpdateNeeded()` on `NXImageLayerVectorDisplay`, not on `NXImageView`.
For ordinary ImageView overlay answers, keep the short `LoadFile(shpPath, out error, ref srIn)` overload from this flow. Do not expand to the property/thread overload unless the user asks about those options.

## Scene Conversion Boundary
- `Xsc.XvcBase2Scene(vectorBase, false, null)` converts vector data to `XScene`; use it for scene/SML conversion flows.
- Do not use `NXImageLayer(scene)` or `SetScene` in ImageView overlay examples unless such an API appears in evidence.

## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.

## Related Pages
- [Vector API Workflow](../../workflows/wf-api-vector.md)
- [Coordinate API Workflow](../../workflows/wf-api-coordinate.md)
- [Spatial Reference and Coordinate Transform](../concepts/spatial-reference-and-coordinate-transform.md)
