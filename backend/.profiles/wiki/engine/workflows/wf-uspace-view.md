---
title: Uspace View Workflow
aliases:
  - Uspace View Workflow
  - wf-uspace-view
  - wf uspace view
symbols:
  - NXUspaceView
  - NXRenderLayer
  - NXCameraState
  - XVertex3d
  - XSpatialReference
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Define region, camera, SR, and interaction mode on NXUspaceView.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXUspaceView.AddRenderLayer`
  - `NXUspaceView.SetSpaceRegion`
  - `NXUspaceView.SetCameraState`
  - `NXUspaceView.RefreshScreen`
  - `NXUspaceView.SetSR`
  - `NXUspaceView.GetSR`
  - `NXUspaceView.SpaceToWorld`
  - `NXUspaceView.SpaceToScreen`
  - `NXUspaceView.GetDrawArgs`
  - `NXUspaceView.SetMouseControlMode`
  - `NXUspaceView.GetMouseControlMode`
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`
- Steps:
  - 공간 범위와 카메라를 먼저 정한다.
  - SR과 레이어를 설정한다.
  - 필요 시 world/screen 변환과 mouse control을 사용한다.

## Required Facts
```yaml
workflow_family: map_view
output_shape: view_shell_or_hosted_control
required_symbols:
  - NXUspaceView.AddRenderLayer
  - NXUspaceView.SetSpaceRegion
  - NXUspaceView.SetCameraState
  - NXUspaceView.RefreshScreen
  - NXUspaceView.SetSR
  - NXUspaceView.GetSR
  - NXUspaceView.SpaceToWorld
  - NXUspaceView.SpaceToScreen
  - NXUspaceView.GetDrawArgs
  - NXUspaceView.SetMouseControlMode
  - NXUspaceView.GetMouseControlMode
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
