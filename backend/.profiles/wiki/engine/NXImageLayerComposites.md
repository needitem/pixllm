---
title: NXImageLayerComposites
aliases:
  - Image Layer Composites
symbols:
  - NXImageLayerComposites
  - XDMCompManager
  - XDMComposite
tags:
  - engine
  - imageview
  - composite
  - xdm
---

# Verified API Facts
- Namespace: `Pixoneer.NXDL.NXImage`
- Type: `public ref class NXImageLayerComposites : public NXImageLayer`
- Verified methods:
  - `GetXDMCompManager()`
  - `Lock()`
  - `UnLock()`
  - `ZoomFit()`
  - `Invalidate()`

# Composite Workflow
- Obtain the composite manager from `GetXDMCompManager()`.
- Clear old composites through the manager.
- Build a new `XDMComposite`.
- Add bands with `SetBand(...)`.
- Add the composite through `XDMCompManager.AddXDMComposite(...)`.
- Refresh the layer/view with `ZoomFit()` and `Invalidate()` where appropriate.

# Important Constraints
- `SetXDMCompManager(...)` is not a verified public API on `NXImageLayerComposites`.
- Treat comment examples as flow hints, not as proof of extra methods.

# Source Anchors
- `Source/NXImage/NXImageLayerComposites.h:123-157`
- `Source/NXDLrs/NXDLrs.h:1864-1880`
- `Source/NXDLgr/XTexture.h:316-345`
