---
title: XDL PlanetView WPF Examples
aliases:
  - XDL_PlanetView1_wpf
  - XDL_PlanetView2_wpf
  - XDL_PlanetView3_wpf
  - XDL_PlanetView4_wpf
symbols:
  - NXPlanetView
  - NXPlanetLayer
  - NXPlanetLayerSceneEditor
  - NXPlanetLayerSceneDisplay
  - XncwObserver
tags:
  - engine
  - workflow
  - samples
  - wpf
  - planet
---

# Overview
- Sample root: `C:/Users/p22418/Documents/Amaranth10/nxdl_example`
- These examples cover planet navigation, measurement, scene editing, and NCW/theater integration.
- Common references:
  - `NXDL`
  - `NXPlanet`
  - optional `NXDLgr`, `NXDLcc`, `NXDLscene`, `NXDLncw`
  - `WindowsFormsIntegration`

# Case Map
- `XDL_PlanetView1_wpf`
  - Core single-view planet shell
  - Initializes camera position and exposes navigation/grid/status toggles
  - Uses `NXPlanetLayer.OnWndProc` to observe interaction

- `XDL_PlanetView2_wpf`
  - Dual 2D/3D planet measurement workflow
  - Sets both 2D and 3D camera positions
  - Covers 2D and 3D toolbox measurement modes separately

- `XDL_PlanetView3_wpf`
  - Scene editing in 2D with display sync in 3D
  - Uses `NXPlanetLayerSceneEditor` and `NXPlanetLayerSceneDisplay`
  - Supports save/load of created scene objects

- `XDL_PlanetView4_wpf`
  - NCW/theater/model integration case
  - Uses `XncwObserver` and theater attachments
  - Extra dialogs observed:
    - `AddPlane.xaml`
    - `PlaneProperty.xaml`
  - Use this as the reference when the user asks for entity/model management, not just base planet hosting

# Delivery Notes
- For WPF planet requests, the sample is often more than `MainWindow.xaml` + code-behind.
- `XDL_PlanetView4_wpf` in particular expects additional dialog XAML files as part of a complete deliverable.
## Structured Page Facts
```yaml
page_family: sample_workflow_examples
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
