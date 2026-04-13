---
title: ImageView XDM Display Workflow
aliases:
  - ImageView XDM load
  - XDM display in ImageView
symbols:
  - NXImageView
  - NXImageLayerComposites
  - XRasterIO
  - XRSLoadFile
  - XDMCompManager
tags:
  - workflow
  - imageview
  - xdm
  - csharp
---

# Verified API Facts
- `NXImageView` is WinForms-backed and should be hosted accordingly in WPF.
- `XRasterIO.Initialize(...)` and `XRasterIO.LoadFile(...)` are the verified file-load entry points.
- `XRSLoadFile.GetBandAt(...)` and `NumBand` support building `XDMComposite`.
- `NXImageLayerComposites` exposes `GetXDMCompManager()`, `Lock()`, `UnLock()`, `ZoomFit()`, and `Invalidate()`.

# Assembly Pattern
1. Host `NXImageView` correctly for your UI technology.
2. Create `XRasterIO` and call `Initialize(...)`.
3. Load the XDM file into `XRSLoadFile^`.
4. Build an `XDMComposite` from one or more `XDMBand` values.
5. Add the composite via `XDMCompManager`.
6. Refresh the image layer/view.

# Do Not Assume
- `SetXDMCompManager(...)` is not verified from declarations.
- A comment example alone is not enough to claim an API is public.
- `SetComposite(...)` seen in examples is usually an app helper, not necessarily a library API.

# Source Anchors
- `Source/NXDLgr/XTexture.h:193-209`
- `Source/NXDLgr/XTexture.h:316-345`
- `Source/NXImage/NXImageView.h:55-120`
- `Source/NXImage/NXImageLayerComposites.h:123-157`
- `Source/NXDLio/NXDLio.h:187-230`
- `Source/NXDLrs/XRSFile.h:962-1035`
