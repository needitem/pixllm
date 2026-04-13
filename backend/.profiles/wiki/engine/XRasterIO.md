---
title: XRasterIO
aliases:
  - RasterIO
symbols:
  - XRasterIO
  - eIOCreateXLDMode
  - LoadFile
tags:
  - engine
  - io
  - raster
  - xdm
---

# Verified API Facts
- Namespace: `Pixoneer.NXDL.NIO`
- Type: `public ref class XRasterIO`
- Verified methods:
  - `Initialize([OutAttribute] String^% strError)`
  - `LoadFile(String^ strFileName, [OutAttribute] String^% strError, bool bCalcStatistics, eIOCreateXLDMode CreateXLD)`
  - additional overloads exist with file key or alternate signatures

# Usage Pattern
- Create `XRasterIO`
- Call `Initialize(...)`
- Call `LoadFile(...)`
- Hold the returned `XRSLoadFile^`

# Source Anchors
- `Source/NXDLio/NXDLio.h:187-230`
- `Source/NXDLio/XRasterIO.cpp:137-203`
- `Source/NXDLgr/XTexture.h:193-209`
