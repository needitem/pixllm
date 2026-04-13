---
title: XDMCompManager
aliases:
  - Composite Manager
symbols:
  - XDMCompManager
  - XDMComposite
  - AddXDMComposite
tags:
  - engine
  - composite
  - xdm
---

# Verified API Facts
- Namespace: `Pixoneer.NXDL.NRS`
- The manager owns `XDMComposite` objects for a layer.
- Verified members:
  - `AddXDMComposite(XDMComposite^% Comp)`
  - `AddXDMCompositeTail(XDMComposite^% Comp)`
  - `GetXDMCompositeAt(int Index)`
  - `RemoveXDMCompositeAll()`
  - `RemoveXDMComposite(XDMComposite^% Comp)`

# Common Pitfall
- The add/remove methods are ref-style managed signatures (`^%`). Treat examples that call them like normal value methods as pseudocode until declaration-backed verification is done.

# Source Anchors
- `Source/NXDLrs/NXDLrs.h:1864-1884`
- `Source/NXDLgr/XTexture.h:316-345`
