---
title: ImageView XDM Display Workflow
aliases:
  - ImageView XDM load display
  - NXImageView XDM display C#
  - c#으로 ImageView를 이용하여 XDM 파일 로드하여 화면에 도시
  - XDM 파일 로드 화면 도시
symbols:
  - NXImageView
  - NXImageLayerComposites
  - XRasterIO
  - XRSLoadFile
  - XDMComposite
  - XDMCompManager
  - AddImageLayer
  - LoadFile
  - GetBandAt
  - SetBand
  - AddXDMComposite
tags:
  - engine
  - workflow
  - imageview
  - xdm
  - csharp
  - winforms
---

# Overview
- Goal: load an XDM-capable raster through `XRasterIO`, build an `XDMComposite`, register it in `NXImageLayerComposites`, and render it through `NXImageView`.
- Minimal verified type chain: `XRasterIO -> XRSLoadFile -> XDMBand -> XDMComposite -> XDMCompManager -> NXImageLayerComposites -> NXImageView`.
- `NXImageView` itself is a WinForms-backed control, so the simplest verified program shape is WinForms. See `Source/NXImage/NXImageView.h:55` and `Source/NXImage/NXImageView.cpp:162`.

# Required Calls
- Initialize raster IO: `XRasterIO.Initialize` -> `Source/NXDLio/NXDLio.h:198`, `Source/NXDLio/XRasterIO.cpp:72`
- Load the file: `XRasterIO.LoadFile` -> `Source/NXDLio/NXDLio.h:222`, `Source/NXDLio/XRasterIO.cpp:137`
- Access loaded bands: `XRSLoadFile.GetBandAt` -> `Source/NXDLrs/XRSFile.h:986`, `Source/NXDLrs/XRSFile.cpp:125`
- Bind bands into a composite: `XDMComposite.SetBand` -> `Source/NXDLrs/NXDLrs.h:1423`, `Source/NXDLrs/XDMComposite.cpp:81`
- Get the composite manager: `NXImageLayerComposites.GetXDMCompManager` -> `Source/NXImage/NXImageLayerComposites.h:149`, `Source/NXImage/NXImageLayerComposites.cpp:66`
- Add the composite: `XDMCompManager.AddXDMComposite` -> `Source/NXDLrs/NXDLrs.h:1867`, `Source/NXDLrs/XDMCompManager.cpp:68`
- Attach the layer to the view: `NXImageView.AddImageLayer` -> `Source/NXImage/NXImageView.h:836`, `Source/NXImage/NXImageView.cpp:162`
- Refresh rendering: `NXImageLayerComposites.ZoomFit` / `Invalidate` -> `Source/NXImage/NXImageLayerComposites.h:142`, `Source/NXImage/NXImageLayerComposites.cpp:56`; `Source/NXImage/NXImageLayerComposites.h:146`, `Source/NXImage/NXImageLayerComposites.cpp:61`

# Verified Steps
1. Create `NXImageView` and `NXImageLayerComposites`.
2. Add the layer to the view through `AddImageLayer(ref layer)`.
3. Create `XRasterIO` and call `Initialize`.
4. Call `LoadFile(path, out error, false, eIOCreateXLDMode.All_NoMsg)` to get `XRSLoadFile`.
5. Create `XDMComposite`.
6. Pull one band for grayscale, or three bands for RGB, using `GetBandAt`.
7. Call `SetBand(ref band, index)` for each band.
8. Call `GetXDMCompManager()` on the composites layer.
9. Lock the layer if you are mutating the manager while rendering is active: `Lock` -> `Source/NXImage/NXImageLayerComposites.h:153`, `Source/NXImage/NXImageLayerComposites.cpp:71`
10. Register the composite with `AddXDMComposite(ref composite)`.
11. Call `ZoomFit()` and `Invalidate()`, then release `UnLock` -> `Source/NXImage/NXImageLayerComposites.h:157`, `Source/NXImage/NXImageLayerComposites.cpp:76`

# Minimal WinForms Program
```csharp
using System;
using System.Windows.Forms;
using Pixoneer.NXDL.NIO;
using Pixoneer.NXDL.NRS;
using Pixoneer.NXDL.NXImage;

public sealed class MainForm : Form
{
    private readonly NXImageView _imageView = new NXImageView();
    private readonly NXImageLayerComposites _compositeLayer = new NXImageLayerComposites();
    private readonly XRasterIO _rasterIo = new XRasterIO();

    public MainForm()
    {
        Text = "XDM ImageView";
        Width = 1280;
        Height = 800;

        _imageView.Dock = DockStyle.Fill;
        Controls.Add(_imageView);

        NXImageLayer layer = _compositeLayer;
        _imageView.AddImageLayer(ref layer);
    }

    public void LoadXdm(string path)
    {
        string error;
        if (!_rasterIo.Initialize(out error))
            throw new InvalidOperationException(error);

        XRSLoadFile loadFile = _rasterIo.LoadFile(path, out error, false, eIOCreateXLDMode.All_NoMsg);
        if (loadFile == null)
            throw new InvalidOperationException(error);

        XDMComposite composite = new XDMComposite();

        XDMBand band0 = loadFile.GetBandAt(0);
        composite.SetBand(ref band0, 0);

        if (loadFile.NumBand >= 3)
        {
            XDMBand band1 = loadFile.GetBandAt(1);
            XDMBand band2 = loadFile.GetBandAt(2);
            composite.SetBand(ref band1, 1);
            composite.SetBand(ref band2, 2);
        }

        XDMCompManager manager = _compositeLayer.GetXDMCompManager();
        _compositeLayer.Lock();
        manager.RemoveXDMCompositeAll();
        manager.AddXDMComposite(ref composite);
        _compositeLayer.ZoomFit();
        _compositeLayer.Invalidate();
        _compositeLayer.UnLock();
    }
}
```

# Notes
- Do not invent an `NXImage.LoadImage(...)` path for this workflow. The verified load entry point here is `XRasterIO.LoadFile`.
- The snippet above is WinForms-first because `NXImageView` is a WinForms control. For WPF hosting, see `workflows/nximageview-wpf-hosting.md`.
- If the file is grayscale, a single `SetBand` call is enough. If the file has three or more channels, fill indices `0`, `1`, and `2`.
