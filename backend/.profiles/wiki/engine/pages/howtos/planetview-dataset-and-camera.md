---
title: PlanetView Dataset and Camera Recipes
description: Common PlanetView tasks for datasets, camera movement, and layer display.
tags:
  - howto
  - planetview
sources:
  - workflows/wf-api-planetview.md
  - workflows/wf-api-dfs.md
---

# PlanetView Dataset and Camera Recipes

## What This Recipe Covers
- Open and register datasets or providers used by `NXPlanetView`.
- Add scene layers and control camera/navigation.
- Separate pure DFS/provider questions from view/render questions.
- Cover capture, render refresh, and planet-specific camera/environment controls.

## Use This Recipe For
- The user asks how to show a dataset in PlanetView.
- The user asks about camera movement, PBI groups, or planet-scene display.
- The user asks about screen capture, sun-follow, or render-layer ordering in PlanetView.

## Minimal C# Flow
Use this shape when the user asks how to add a render layer to `NXPlanetView` and refresh the view. The layer and optional camera target are supplied by the caller; do not use ellipsis placeholders for them.

```csharp
bool AddPlanetRenderLayer(NXPlanetView planetView, NXRenderLayer renderLayer)
{
    if (planetView == null || renderLayer == null)
        return false;

    NXRenderLayer layer = renderLayer;
    bool added = planetView.AddRenderLayer(ref layer);
    if (added)
        planetView.RefreshScreen();

    return added;
}

bool MovePlanetCameraToTarget(
    NXPlanetView planetView,
    XGeoPoint target,
    double distance,
    XAngle azimuth,
    XAngle elevation)
{
    if (planetView == null || target == null || azimuth == null || elevation == null)
        return false;

    bool moved = planetView.LookTarget(target, distance, azimuth, elevation);
    if (moved)
        planetView.RefreshScreen();

    return moved;
}
```

Use `AddRenderLayer(ref layer)` for layer attach and `RefreshScreen()` for immediate redraw. Use `LookTarget` or `SetCameraPosition` only when the user asks for camera movement or provides the camera target/state.

## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.

## Common Recipes
- `dataset 연결`
  A common PlanetView dataset flow registers provider groups through `NXPlanetEngine.AddPBIGroup`, then sets the default dataset on `NXPlanetView`.
- `카메라 설정`
  Use `SetCameraPosition` for quick placement, and `SetCameraState` when the full state object already exists.
- `화면 갱신`
  Use `RefreshScreen`, `RefreshBaseMap`, or `RefreshLOD` depending on whether the user changed view, terrain source, or detail state.
- `캡처`
  Use `CaptureScreen` for the current framebuffer, and `CaptureScreenByBlock` for tiled/export-like capture.
- `효과/환경`
  Use `SetSunFollowCamera`, `SetSunPosition`, and `SetLightingFactor` for environment-lighting answers rather than treating them as generic shader settings.

## Related Pages
- [PlanetView API Workflow](../../workflows/wf-api-planetview.md)
- [DFS API Workflow](../../workflows/wf-api-dfs.md)
- [Provider, Dataset, and Scene Assets](../concepts/provider-dataset-and-scene-assets.md)
