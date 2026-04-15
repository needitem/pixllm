---
title: Planet View Workflow
aliases:
  - Planet View Workflow
  - wf-planet-view
  - wf planet view
symbols:
  - NXPlanetView
  - NXPlanetLayer
  - NXRenderLayer
  - NXCameraState
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Create NXPlanetView, set camera state, and attach render layers.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXPlanetView.SetCameraPosition`
  - `NXPlanetView.SetCameraState`
  - `NXPlanetView.AddRenderLayer`
  - `NXPlanetView.GetDrawArgs`
  - `NXPlanetView.CaptureScreen`
  - `NXPlanetView.SetMouseControlMode`
  - `NXPlanetView.ChangeLayerOrder`
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`
- Steps:
  - 뷰를 생성한다.
  - 카메라를 설정한다.
  - 렌더 레이어를 추가한다.
  - 필요 시 draw args/capture/mouse control을 사용한다.

## Required Facts
```yaml
workflow_family: map_view
output_shape: view_shell_or_hosted_control
required_symbols:
  - NXPlanetView.SetCameraPosition
  - NXPlanetView.SetCameraState
  - NXPlanetView.AddRenderLayer
  - NXPlanetView.GetDrawArgs
  - NXPlanetView.CaptureScreen
  - NXPlanetView.SetMouseControlMode
  - NXPlanetView.ChangeLayerOrder
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
  - [xdl-planetview-wpf-examples.md](xdl-planetview-wpf-examples.md)
