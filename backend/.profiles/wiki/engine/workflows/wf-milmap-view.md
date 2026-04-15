---
title: Milmap View Workflow
aliases:
  - Milmap View Workflow
  - wf-milmap-view
  - wf milmap view
symbols:
  - NXMilmapView
  - NXMilmapLayer
  - NXRenderLayer
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Control scale, center, layers, draw args, and capture on NXMilmapView.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXMilmapView.CheckMilmapData`
  - `NXMilmapView.SetGeoToCenter`
  - `NXMilmapView.SearchScale`
  - `NXMilmapView.Zoom`
  - `NXMilmapView.ZoomFitRect`
  - `NXMilmapView.IsExistScale`
  - `NXMilmapView.SearchName`
  - `NXMilmapView.ShowCross`
  - `NXMilmapView.RefreshScreen`
  - `NXMilmapView.AddRenderLayer`
  - `NXMilmapView.ChangeLayerOrder`
  - `NXMilmapView.GetDrawArgs`
  - `NXMilmapView.CaptureScreen`
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`
- Steps:
  - 데이터/축척 가능 여부를 확인한다.
  - SetGeoToCenter나 Zoom 계열로 위치를 맞춘다.
  - 레이어를 붙이고 필요 시 순서를 바꾼다.
  - draw args/capture/crosshair를 쓴다.

## Required Facts
```yaml
workflow_family: map_view
output_shape: view_shell_or_hosted_control
required_symbols:
  - NXMilmapView.CheckMilmapData
  - NXMilmapView.SetGeoToCenter
  - NXMilmapView.SearchScale
  - NXMilmapView.Zoom
  - NXMilmapView.ZoomFitRect
  - NXMilmapView.IsExistScale
  - NXMilmapView.SearchName
  - NXMilmapView.ShowCross
  - NXMilmapView.RefreshScreen
  - NXMilmapView.AddRenderLayer
  - NXMilmapView.ChangeLayerOrder
  - NXMilmapView.GetDrawArgs
  - NXMilmapView.CaptureScreen
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```

## Output Guidance
- Explanation requests: summarize the view initialization order, layer wiring, camera/state setup, and refresh path.
- Code/sample requests: return the host/view shell plus the ordered initialization sequence for layers, SR, and interaction state.
- If the user asks for WPF, include the XAML shell and code-behind instead of returning only a single `.cs` file.

## Common Wrong Patterns
- Do not invent helper methods or short overloads outside the verified symbol set above.
- Do not convert verified methods into properties, or properties into methods, without source proof.
- Do not guess `ref`/`out`, enum literals, or return types from naming alone.
- Do not skip prerequisites implied by the ordered call chain in this workflow.
- Do not skip the camera/state or layer setup steps when the question is about a runnable map/planet/uspace workflow.

- See also:
  - [xdl-milmapview-wpf-examples.md](xdl-milmapview-wpf-examples.md)
