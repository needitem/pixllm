---
title: XDL Data Structure and GeoPosition WPF Examples
aliases:
  - XDL_DataStructure_wpf
  - XDL_GeoPosition_wpf
  - XGeoPoint example wpf
symbols:
  - XAngle
  - XVertex2i
  - XVertex2d
  - XVertex3d
  - XVertex4d
  - XGeoPoint
  - Xfn
tags:
  - engine
  - workflow
  - samples
  - wpf
  - geometry
---

# Overview
- Sample root: `C:/Users/p22418/Documents/Amaranth10/nxdl_example`
- These examples are lightweight WPF button-driven demos for primitive NXDL data types and coordinate conversion helpers.
- Project references are minimal compared with the visual-control families. The observed `csproj` files mainly reference `NXDL` plus standard WPF assemblies.

# Cases
- `XDL_DataStructure_wpf`
  - WPF shell with a grid of buttons for `XAngle`, `XVertex2i`, `XVertex2d`, `XVertex3d`, `XVertex4d`, `XGeoPoint`, `XColorTable`, and `XGrid`
  - Good reference when the user asks for "how do I construct or inspect basic NXDL structs/classes in C#"
  - The code-behind demonstrates direct construction, conversion, equality checks, and console output

- `XDL_GeoPosition_wpf`
  - Focused on geographic math rather than UI hosting
  - Observed operations:
    - bearing + distance based position calculation
    - arc distance / angle between positions
    - geo to ECEF conversion
    - ECEF to geo conversion
  - Primary symbols: `XGeoPoint`, `Xfn.GeoToEcr`, `Xfn.EcrToGeo`

# Delivery Notes
- For these cases, a small WPF window with buttons is faithful to the examples.
- Unlike the image/milmap/planet/video families, these samples do not require `WindowsFormsHost`.
- If the user asks only for the math API usage, you may answer with focused code snippets, but for a runnable WPF sample keep:
  - `App.xaml`
  - `App.xaml.cs`
  - `MainWindow.xaml`
  - `MainWindow.xaml.cs`
