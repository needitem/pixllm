---
title: NXImageView
aliases:
  - ImageView
symbols:
  - NXImageView
  - NXImageViewDrawArgs
tags:
  - engine
  - imageview
  - ui
  - winforms
---

# Verified API Facts
- Namespace: `Pixoneer.NXDL.NXImage`
- Type: `public ref class NXImageView : public System::Windows::Forms::Panel`
- The control is a WinForms panel-backed engine view. It is not a pure WPF control.

# Integration Notes
- In WPF, host `NXImageView` through `WindowsFormsHost`.
- `NXImageView` works with layers such as `NXImageLayerComposites`.
- Direct WPF `Grid.Children.Add(nxImageView)` style usage is not a verified integration path.

# Related Types
- `NXImageLayerComposites`
- `NXImageViewDrawArgs`
- `XRasterIO`
- `XRSLoadFile`

# Source Anchors
- `Source/NXImage/NXImageView.h:55-120`
- `Source/NXImage/NXImageView.cpp:1248-1310`
- `Source/NXDLgr/XTexture.h:134-148`
