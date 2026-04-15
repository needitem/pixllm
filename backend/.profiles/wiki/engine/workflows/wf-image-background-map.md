---
title: Image Background Map Workflow
aliases:
  - Image Background Map Workflow
  - wf-image-background-map
  - wf image background map
symbols:
  - NXImageView
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Configure background-map settings on NXImageView.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXImageView.SetBackgroundMap`
  - `NXImageView.BackgroundMapVisible`
  - `NXImageView.BackgroundMapAlpha`
  - `NXImageView.BackgroundMapContrast`
  - `NXImageView.BackgroundMapBrightness`
  - `NXImageView.BackgroundMapSaturation`
  - `NXImageView.BackgroundMapInterpolPixel`
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`
- Steps:
  - SetBackgroundMap으로 배경지도를 연결한다.
  - BackgroundMap 속성으로 표시/화질을 조절한다.
  - 화면 갱신을 수행한다.

## Required Facts
```yaml
workflow_family: image_view
output_shape: view_shell_or_hosted_control
required_symbols:
  - NXImageView.SetBackgroundMap
  - NXImageView.BackgroundMapVisible
  - NXImageView.BackgroundMapAlpha
  - NXImageView.BackgroundMapContrast
  - NXImageView.BackgroundMapBrightness
  - NXImageView.BackgroundMapSaturation
  - NXImageView.BackgroundMapInterpolPixel
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
