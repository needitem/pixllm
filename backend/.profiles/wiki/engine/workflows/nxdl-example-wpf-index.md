---
title: NXDL Example WPF Index
aliases:
  - nxdl_example
  - nxdl example wpf
  - Amaranth10 nxdl examples
symbols:
  - NXImageView
  - NXMilmapView
  - NXPlanetView
  - NXVideoView
  - XGeoPoint
tags:
  - engine
  - workflow
  - samples
  - wpf
---

# Overview
- Sample root observed for this index: `C:/Users/p22418/Documents/Amaranth10/nxdl_example`
- The example tree contains WPF-first samples for data structures, geographic math, image display, milmap, planet, and video workflows.
- Every observed WPF sample keeps the standard shell shape:
  - `App.xaml`
  - `App.xaml.cs`
  - `MainWindow.xaml`
  - `MainWindow.xaml.cs`
  - matching `.csproj`
- Some advanced samples add extra dialogs or helper XAML files. Treat those as part of the expected deliverable when reproducing the workflow.

# Families
- Data structures and geographic math:
  - See [xdl-datastructure-geoposition-wpf-examples.md](xdl-datastructure-geoposition-wpf-examples.md)
  - Samples: `XDL_DataStructure_wpf`, `XDL_GeoPosition_wpf`

- Image display and raster workflows:
  - See [xdl-imageview-wpf-examples.md](xdl-imageview-wpf-examples.md)
  - Samples: `XDL_ImageView1_wpf` through `XDL_ImageView6_wpf`

- Milmap workflows:
  - See [xdl-milmapview-wpf-examples.md](xdl-milmapview-wpf-examples.md)
  - Samples: `XDL_MilmapView01_wpf` through `XDL_MilmapView03_wpf`

- Planet workflows:
  - See [xdl-planetview-wpf-examples.md](xdl-planetview-wpf-examples.md)
  - Samples: `XDL_PlanetView1_wpf` through `XDL_PlanetView4_wpf`

- Video workflows:
  - See [xdl-videoview-wpf-examples.md](xdl-videoview-wpf-examples.md)
  - Samples: `XDL_VideoView01_wpf` through `XDL_VideoView05_wpf`

# Delivery Rule
- When a user asks for one of these WPF workflows, prefer the sample shape from `nxdl_example`:
  - XAML window shell
  - matching code-behind
  - project file when the request is for a runnable sample/app
- Do not collapse these examples into a single `.cs` file unless the user explicitly asks for a code-behind-only sketch.
## Structured Page Facts
```yaml
page_family: sample_index
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
