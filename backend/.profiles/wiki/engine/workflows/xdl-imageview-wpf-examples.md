---
title: XDL ImageView WPF Examples
aliases:
  - XDL_ImageView1_wpf
  - XDL_ImageView2_wpf
  - XDL_ImageView3_wpf
  - XDL_ImageView4_wpf
  - XDL_ImageView5_wpf
  - XDL_ImageView6_wpf
symbols:
  - NXImageView
  - NXImageLayerComposites
  - NXImageLayerCompLink
  - NXImageLayerVectorEditor
  - XRSLoadFile
  - XDMComposite
  - XDMCompManager
tags:
  - engine
  - workflow
  - samples
  - wpf
  - imageview
---

# Overview
- Sample root: `C:/Users/p22418/Documents/Amaranth10/nxdl_example`
- All observed ImageView WPF examples use `WindowsFormsHost` to host NXDL WinForms-backed controls inside a WPF shell.
- Common references in the project files:
  - `NXDL`
  - `NXDLio`
  - `NXDLrs`
  - `NXImage`
  - `WindowsFormsIntegration`
- These are the closest practical references for "WPF + ImageView + raster display" questions.

# Common File Shape
- `App.xaml`
- `App.xaml.cs`
- `MainWindow.xaml`
- `MainWindow.xaml.cs`
- `.csproj`
- Optional extra dialogs or helper XAML in advanced cases

# Case Map
- `XDL_ImageView1_wpf`
  - Basic single-view raster load and composite registration
  - Loads a raster through `XRasterIO.LoadFile`
  - Gets `XDMCompManager` from `NXImageLayerComposites`
  - Creates and registers an `XDMComposite`

- `XDL_ImageView2_wpf`
  - Dual-view workflow
  - Uses two `NXImageLayerComposites` layers and two loaded rasters
  - Includes a spatial-filter action and a "show original image" path

- `XDL_ImageView3_wpf`
  - Linked comparison layout
  - Uses `NXImageLayerCompLink`
  - Shows two composite managers side by side / linked for comparison

- `XDL_ImageView4_wpf`
  - Focused composite-construction helper
  - Explicit `CreateComposite(XRSLoadFile, band0, band1, band2)` pattern
  - Useful when the user asks for band-to-composite wiring

- `XDL_ImageView5_wpf`
  - Adds background map integration on top of the image view
  - Uses `SetBackgroundMap(...)`
  - Includes menu actions to show/hide the background view

- `XDL_ImageView6_wpf`
  - Most advanced ImageView sample in this set
  - Adds vector editing and vector import/export flows
  - Includes menus for point/line/ellipse/rectangle/polyline/polygon/text tools
  - Includes measurement and property-edit actions
  - Extra dialog observed: `PropertyXvcObj.xaml`

# Usage Notes
- For WPF answers, keep the XAML shell and `WindowsFormsHost`; these examples are not code-behind-only samples.
- For the core raster/XDM path, also see:
  - [imageview-xdm-display-workflow.md](imageview-xdm-display-workflow.md)
  - [nximageview-wpf-hosting.md](nximageview-wpf-hosting.md)
