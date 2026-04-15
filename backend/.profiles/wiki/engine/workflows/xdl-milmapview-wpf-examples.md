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
