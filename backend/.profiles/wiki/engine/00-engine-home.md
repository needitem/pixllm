---
title: PIXLLM Engine Wiki
aliases:
  - Engine Knowledge Base
symbols:
  - NXImageView
  - XRasterIO
  - XRSLoadFile
  - NXImageLayerComposites
  - XDMCompManager
tags:
  - engine
  - imageview
  - xdm
  - api
---

# Overview
This wiki is a compiled knowledge layer for the PIXLLM engine/runtime. It is not the source of truth. Use it to orient quickly, then verify generated code against declaration and implementation evidence from the engine source tree.

# Verified API Facts
- `Pixoneer.NXDL.NXImage.NXImageView` is a `System::Windows::Forms::Panel`, not a native WPF control.
- `Pixoneer.NXDL.NIO.XRasterIO` exposes `Initialize(...)` and `LoadFile(...)`.
- `Pixoneer.NXDL.NRS.XRSLoadFile` represents a loaded raster file and exposes `GetBandAt(...)`.
- `Pixoneer.NXDL.NXImage.NXImageLayerComposites` exposes `GetXDMCompManager()`, `Lock()`, `UnLock()`, `ZoomFit()`, and `Invalidate()`.
- `Pixoneer.NXDL.NRS.XDMCompManager` exposes `AddXDMComposite(XDMComposite^% Comp)`, `GetXDMCompositeAt(...)`, and `RemoveXDMCompositeAll()`.

# Usage Guidance
- Use this wiki to discover the right objects and high-level flow.
- Do not invent API names from examples alone.
- For code generation, prefer declaration and implementation evidence over comment examples.

# Source Anchors
- `Source/NXImage/NXImageView.h:55-120`
- `Source/NXImage/NXImageLayerComposites.h:123-157`
- `Source/NXDLio/NXDLio.h:187-230`
- `Source/NXDLrs/XRSFile.h:962-1035`
- `Source/NXDLrs/NXDLrs.h:1860-1880`
