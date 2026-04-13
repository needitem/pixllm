---
title: XRSLoadFile
aliases:
  - Loaded Raster File
symbols:
  - XRSLoadFile
  - GetBandAt
  - NumBand
tags:
  - engine
  - raster
  - xdm
  - bands
---

# Verified API Facts
- Namespace: `Pixoneer.NXDL.NRS`
- Type: `public ref class XRSLoadFile`
- Verified members:
  - `GetBandAt(int nIndex)`
  - `NumBand`
  - `FileName`
  - other geographic/statistical helpers

# Usage Pattern
- `XRasterIO.LoadFile(...)` returns `XRSLoadFile^`
- Use `GetBandAt(...)` to access `XDMBand`
- Use `NumBand` to decide grayscale vs RGB composition logic

# Source Anchors
- `Source/NXDLrs/XRSFile.h:962-1035`
- `Source/NXDLgr/XTexture.h:323-345`
