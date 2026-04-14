---
title: XDL MilmapView WPF Examples
aliases:
  - XDL_MilmapView01_wpf
  - XDL_MilmapView02_wpf
  - XDL_MilmapView03_wpf
symbols:
  - NXMilmapView
  - NXMilmapLayer
  - NXMilmapLayerSceneEditor
  - NXMilmapLayerSceneDisplay
tags:
  - engine
  - workflow
  - samples
  - wpf
  - milmap
---

# Overview
- Sample root: `C:/Users/p22418/Documents/Amaranth10/nxdl_example`
- These examples cover milmap navigation, measurement, and scene editing.
- Common references:
  - `NXDL`
  - `NXMilmap`
  - optional `NXDLgr`, `NXDLcc`, `NXDLscene`
  - `WindowsFormsIntegration`

# Case Map
- `XDL_MilmapView01_wpf`
  - Core milmap navigation shell
  - Initializes `NXMilmapView.m_MapEngine` from `XMilmapConfig.xml`
  - Covers inverse mouse controls, center move, grid mode, rotation mode, zoom mode, PBP/cross toggles

- `XDL_MilmapView02_wpf`
  - Measurement-focused workflow
  - Uses toolbox modes for:
    - line distance
    - polyline distance
    - area
    - angle
    - circle
  - Includes custom render / wndproc hooks

- `XDL_MilmapView03_wpf`
  - Scene editing and scene display sync
  - Uses `NXMilmapLayerSceneEditor` + `NXMilmapLayerSceneDisplay`
  - Supports point / polyline / polygon / circle / symbol creation
  - Saves scene content to file and reloads it into a second view

# Delivery Notes
- Keep the WPF shell, toolbar/menu wiring, and `WindowsFormsHost`.
- For scene-editing requests, `XDL_MilmapView03_wpf` is the strongest reference because it shows both edit and display lanes together.
