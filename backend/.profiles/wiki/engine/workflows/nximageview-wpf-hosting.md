---
title: NXImageView WPF Hosting
aliases:
  - NXImageView WPF
  - WindowsFormsHost NXImageView
  - ImageView WPF hosting
symbols:
  - NXImageView
  - WindowsFormsHost
  - NXImageLayerComposites
tags:
  - engine
  - workflow
  - imageview
  - wpf
  - csharp
---

# Overview
- `NXImageView` is a WinForms-backed control, not a native WPF control.
- Verified type declaration: `Source/NXImage/NXImageView.h:55`
- Use `System.Windows.Forms.Integration.WindowsFormsHost` when the application shell is WPF.
- For generic C# desktop program generation, prefer this WPF shell pattern first and only fall back to a pure WinForms form when the user explicitly asks for WinForms.

# Verified Hosting Pattern
- Create `WindowsFormsHost`.
- Create `NXImageView`.
- Assign `host.Child = imageView`.
- Create `NXImageLayerComposites`.
- Add the layer to the view through `NXImageView.AddImageLayer` -> `Source/NXImage/NXImageView.h:836`, `Source/NXImage/NXImageView.cpp:162`

# WPF Output Rule
- Treat WPF as a XAML-first delivery target.
- When generating a new WPF sample or app, include the visual shell and its code-behind together rather than returning only a single `.cs` file.
- Minimum expected file set:
  - `MainWindow.xaml`
  - `MainWindow.xaml.cs`
  - `App.xaml`
  - `App.xaml.cs`
- Include the `.csproj` too when the request is for a runnable sample/app from scratch.

# Minimal WPF Host Snippet
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

```csharp
using System.Windows;
using System.Windows.Forms.Integration;
using Pixoneer.NXDL.NXImage;

public partial class MainWindow : Window
{
    private readonly NXImageView _imageView = new NXImageView();
    private readonly NXImageLayerComposites _compositeLayer = new NXImageLayerComposites();

    public MainWindow()
    {
        InitializeComponent();

        var host = new WindowsFormsHost
        {
            Child = _imageView
        };

        NXImageLayer layer = _compositeLayer;
        _imageView.AddImageLayer(ref layer);

        Content = host;
    }
}
```

# Notes
- Keep `UseWindowsForms=true` because the hosted child is still `NXImageView`.
- Once hosted, the actual XDM loading flow is still the same as the WinForms workflow. See `workflows/imageview-xdm-display-workflow.md`.
- If the user asks only for the shortest possible interop sample, WinForms remains the most direct path. If the user asks for the default desktop shell, prefer WPF.
- If the request says WPF, a response that omits XAML should be treated as incomplete unless the user explicitly asks for code-behind only.
- This page is intended as verified API guidance. It should not imply that the desktop agent must run standalone compile checks before producing an answer.
## Structured Page Facts
```yaml
page_family: hosting_workflow
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
