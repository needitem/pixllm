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
  - wpf
  - winforms
---

# Overview
- Goal: load an XDM-capable raster through `XRasterIO`, build an `XDMComposite`, register it in `NXImageLayerComposites`, and render it through `NXImageView`.
- Minimal verified type chain: `XRasterIO -> XRSLoadFile -> XDMBand -> XDMComposite -> XDMCompManager -> NXImageLayerComposites -> NXImageView`.
- `NXImageView` itself is a WinForms-backed control. For new C# desktop programs, prefer a WPF shell that hosts it through `WindowsFormsHost`; use a pure WinForms form only when the user explicitly asks for WinForms. See `Source/NXImage/NXImageView.h:55` and `Source/NXImage/NXImageView.cpp:162`.

# Required Calls
- Initialize raster IO: `XRasterIO.Initialize` -> `Source/NXDLio/NXDLio.h:198`, `Source/NXDLio/XRasterIO.cpp:72`
- Load the file: `XRasterIO.LoadFile` -> `Source/NXDLio/NXDLio.h:222`, `Source/NXDLio/XRasterIO.cpp:137`
- Access loaded bands: `XRSLoadFile.GetBandAt` -> `Source/NXDLrs/XRSFile.h:986`, `Source/NXDLrs/XRSFile.cpp:125`
- Bind bands into a composite: `XDMComposite.SetBand` -> `Source/NXDLrs/NXDLrs.h:1423`, `Source/NXDLrs/XDMComposite.cpp:81`
- Get the composite manager: `NXImageLayerComposites.GetXDMCompManager` -> `Source/NXImage/NXImageLayerComposites.h:149`, `Source/NXImage/NXImageLayerComposites.cpp:66`
- Add the composite: `XDMCompManager.AddXDMComposite` -> `Source/NXDLrs/NXDLrs.h:1867`, `Source/NXDLrs/XDMCompManager.cpp:68`
- Attach the layer to the view: `NXImageView.AddImageLayer` -> `Source/NXImage/NXImageView.h:836`, `Source/NXImage/NXImageView.cpp:162`
- Refresh rendering: `NXImageLayerComposites.ZoomFit` / `Invalidate` -> `Source/NXImage/NXImageLayerComposites.h:142`, `Source/NXImage/NXImageLayerComposites.cpp:56`; `Source/NXImage/NXImageLayerComposites.h:146`, `Source/NXImage/NXImageLayerComposites.cpp:61`

# Verified Workflow Source Anchors
- `NXImageView` control host: `Source/NXImage/NXImageView.h:55`, `Source/NXImage/NXImageView.cpp:162`
- `NXImageLayerComposites` display layer: `Source/NXImage/NXImageLayerComposites.h:122`, `Source/NXImage/NXImageLayerComposites.cpp:56`
- `XRasterIO` initialization and file load: `Source/NXDLio/NXDLio.h:198`, `Source/NXDLio/NXDLio.h:222`, `Source/NXDLio/XRasterIO.cpp:102`
- `XRSLoadFile` band access: `Source/NXDLrs/XRSFile.h:986`, `Source/NXDLrs/XRSFile.cpp:125`
- `XDMComposite` band binding: `Source/NXDLrs/NXDLrs.h:1423`, `Source/NXDLrs/XDMComposite.cpp:81`
- `XDMCompManager` composite registration: `Source/NXDLrs/NXDLrs.h:1867`, `Source/NXDLrs/XDMCompManager.cpp:68`

# Verified Steps
1. Create a WPF `Window` with `System.Windows.Forms.Integration.WindowsFormsHost`.
2. Create `NXImageView` and `NXImageLayerComposites`.
3. Assign `host.Child = imageView`, then add the layer through `AddImageLayer(ref layer)`.
4. Create `XRasterIO` and call `Initialize`.
5. Call `LoadFile(path, out error, false, eIOCreateXLDMode.All_NoMsg)` to get `XRSLoadFile`.
6. Create `XDMComposite`.
7. Pull one band for grayscale, or three bands for RGB, using `GetBandAt`.
8. Call `SetBand(ref band, index)` for each band.
9. Call `GetXDMCompManager()` on the composites layer.
10. Lock the layer if you are mutating the manager while rendering is active: `Lock` -> `Source/NXImage/NXImageLayerComposites.h:153`, `Source/NXImage/NXImageLayerComposites.cpp:71`
11. Register the composite with `AddXDMComposite(ref composite)`.
12. Call `ZoomFit()` and `Invalidate()`, then release `UnLock` -> `Source/NXImage/NXImageLayerComposites.h:157`, `Source/NXImage/NXImageLayerComposites.cpp:76`

# WPF Delivery Rule
- If the user asks for a WPF solution, the default deliverable is a XAML-based window, not a single C# file.
- Prefer at least these files together:
  - `MainWindow.xaml`
  - `MainWindow.xaml.cs`
  - `App.xaml`
  - `App.xaml.cs`
  - the matching `.csproj` when a fresh sample/app is being created
- A single `.cs` file is acceptable only for pure WinForms examples or when the user explicitly says they do not want XAML.

# Preferred WPF Program Shape
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net8.0-windows</TargetFramework>
    <UseWPF>true</UseWPF>
    <UseWindowsForms>true</UseWindowsForms>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
```

```xml
<Window x:Class="XdmViewer.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:wf="clr-namespace:System.Windows.Forms.Integration;assembly=WindowsFormsIntegration"
        Title="XDM ImageView"
        Width="1280"
        Height="800">
  <Grid>
    <wf:WindowsFormsHost x:Name="ImageHost" />
  </Grid>
</Window>
```

```csharp
using System;
using System.Windows;
using Pixoneer.NXDL.NIO;
using Pixoneer.NXDL.NRS;
using Pixoneer.NXDL.NXImage;

namespace XdmViewer;

public partial class MainWindow : Window
{
    private readonly NXImageView _imageView = new();
    private readonly NXImageLayerComposites _compositeLayer = new();
    private readonly XRasterIO _rasterIo = new();

    public MainWindow()
    {
        InitializeComponent();

        ImageHost.Child = _imageView;

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

# Explicit WinForms Variant
```csharp
using System.Windows.Forms;
using Pixoneer.NXDL.NXImage;

public sealed class MainForm : Form
{
    private readonly NXImageView _imageView = new NXImageView();

    public MainForm()
    {
        _imageView.Dock = DockStyle.Fill;
        Controls.Add(_imageView);
    }
}
```

# Notes
- Do not invent an `NXImage.LoadImage(...)` path for this workflow. The verified load entry point here is `XRasterIO.LoadFile`.
- Keep `UseWindowsForms=true` even in the preferred WPF shape because `NXImageView` is still a WinForms control under `WindowsFormsHost`.
- Prefer the WPF shell above when the user asks for a generic C# desktop program. Use the WinForms variant only when WinForms is explicitly requested.
- For WPF answers, do not stop at a single code-behind class. Include the XAML shell that hosts `WindowsFormsHost`.
- For focused hosting details, see `workflows/nximageview-wpf-hosting.md`.
- If the file is grayscale, a single `SetBand` call is enough. If the file has three or more channels, fill indices `0`, `1`, and `2`.
- These workflow notes are reference guidance, not a requirement to pass a standalone compile gate before answering.
- If some signatures remain uncertain, prefer calling out the uncertainty from verified source excerpts instead of blocking on compile-oriented verification.

# Common Pitfalls
- Do not use `XRasterIO.LoadFile(path)` with a made-up short overload. The verified workflow here is `LoadFile(path, out error, false, eIOCreateXLDMode.All_NoMsg)`.
- Do not replace `out error` with `ref error` unless the verified signature explicitly says `ref`.
- Do not use `GetXDMCompManager` like a property. In this workflow it is a method call: `GetXDMCompManager()`.
- Do not pass `NXImageLayerComposites` directly to `AddImageLayer(ref ...)` without the verified base-layer pattern. Use `NXImageLayer layer = compositeLayer; imageView.AddImageLayer(ref layer);`.
- Do not leave a fake path like `C:\\path\\to\\your\\file.xdm` in an auto-executed code path. Either parameterize the path, open a file dialog, or leave the example path in a commented usage snippet instead of calling it automatically.
- If you define WinForms handlers such as `Form_Load` or `FormClosing`, wire them in `InitializeComponent()` or remove the dead handlers. Unwired handlers are treated as an incomplete interaction path.
## Structured Page Facts
```yaml
page_family: curated_workflow
role: curated_reference
verification_rules:
  - use_this_page_when_the_question_matches_its_scenario_scope
  - cross_check_methods_pages_before_emitting_exact_call_shapes
  - keep_output_shape_rules_from_this_page_when_present
```

## Runtime Usage
- Use this page as a richer scenario-level reference than the normalized `wf-*.md` pages when the question clearly matches this scenario.
- If this page defines output-shape constraints such as WPF/XAML delivery, keep those constraints in the final answer.
- Do not use sample-driven code patterns here to override conflicting exact signatures from methods pages.
