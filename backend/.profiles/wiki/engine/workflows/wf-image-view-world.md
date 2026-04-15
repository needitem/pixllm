---
title: Image View World Workflow
aliases:
  - Image View World Workflow
  - wf-image-view-world
  - wf image view world
symbols:
  - NXImageView
  - XVertex2d
  - XAngle
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Control zoom and world state on NXImageView.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXImageView.ZoomFit`
  - `NXImageView.ZoomOneToOne`
  - `NXImageView.ZoomFitRect`
  - `NXImageView.SetWorld`
  - `NXImageView.SetWorldToCenter`
  - `NXImageView.SetWorldPerScreen`
  - `NXImageView.LinkCameraFrom`
  - `NXImageView.RefreshScreen`
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`
- Steps:
  - fit/zoom/world-set 목적을 먼저 정한다.
  - 해당 NXImageView 메서드를 호출한다.
  - 멀티뷰면 LinkCameraFrom을 쓴다.
  - 필요 시 RefreshScreen으로 반영한다.

## Required Facts
```yaml
workflow_family: image_view
output_shape: view_shell_or_hosted_control
required_symbols:
  - NXImageView.ZoomFit
  - NXImageView.ZoomOneToOne
  - NXImageView.ZoomFitRect
  - NXImageView.SetWorld
  - NXImageView.SetWorldToCenter
  - NXImageView.SetWorldPerScreen
  - NXImageView.LinkCameraFrom
  - NXImageView.RefreshScreen
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```

## Output Guidance
- Explanation requests: summarize the host control, layer attachment order, and the exact display/update path.
- Code/sample requests: include the host/view/layer wiring first, then the data-load/composite path.
- If the user asks for WPF, include the XAML shell and code-behind instead of returning only a single `.cs` file.

## Common Wrong Patterns
- Do not invent helper methods or short overloads outside the verified symbol set above.
- Do not convert verified methods into properties, or properties into methods, without source proof.
- Do not guess `ref`/`out`, enum literals, or return types from naming alone.
- Do not skip prerequisites implied by the ordered call chain in this workflow.
- Do not return only an isolated view call when the actual workflow depends on layer attachment and display/update steps.
