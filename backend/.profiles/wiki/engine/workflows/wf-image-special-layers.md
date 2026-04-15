---
title: Image Special Layers Workflow
aliases:
  - Image Special Layers Workflow
  - wf-image-special-layers
  - wf image special layers
symbols:
  - NXImageLayerCompLink
  - NXImageLayerStereoComposites
  - NXImageView
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Use comparison and stereo image layers.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXImageLayerCompLink.ZoomFit`
  - `NXImageLayerStereoComposites.GetXDMCompManagerL`
  - `NXImageLayerStereoComposites.GetXDMCompManagerR`
  - `NXImageLayerStereoComposites.ZoomFit`
  - `NXImageView.StereoViewType`
  - `NXImageView.StereoColorMaskL`
  - `NXImageView.StereoColorMaskR`
- Verified source:
  - `Source/NXImage/NXImageLayerCompLink.h:151`
  - `Source/NXImage/NXImageLayerCompLink.h:192`
  - `Source/NXImage/NXImageLayerStereoComposites.h:54`
  - `Source/NXImage/NXImageLayerStereoComposites.h:69`
  - `Source/NXImage/NXImageLayerStereoComposites.h:77`
  - `Source/NXImage/NXImageLayerStereoComposites.h:146`
  - `Source/NXImage/NXImageLayerStereoComposites.h:150`
  - `Source/NXImage/NXImageLayerStereoComposites.h:218`
- Steps:
  - 특수 레이어를 일반 이미지 레이어처럼 붙인다.
  - comp-link 또는 stereo 전용 설정을 적용한다.
  - 좌우 manager와 view stereo 속성을 맞춘다.

## Required Facts
```yaml
workflow_family: image_view
output_shape: view_shell_or_hosted_control
required_symbols:
  - NXImageLayerCompLink.ZoomFit
  - NXImageLayerStereoComposites.GetXDMCompManagerL
  - NXImageLayerStereoComposites.GetXDMCompManagerR
  - NXImageLayerStereoComposites.ZoomFit
  - NXImageView.StereoViewType
  - NXImageView.StereoColorMaskL
  - NXImageView.StereoColorMaskR
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
