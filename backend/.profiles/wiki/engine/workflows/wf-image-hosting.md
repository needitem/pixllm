---
title: Image Hosting Workflow
aliases:
  - Image Hosting Workflow
  - wf-image-hosting
  - wf image hosting
symbols:
  - NXImageView
  - NXImageLayer
  - NXImageLayerComposites
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Host NXImageView and attach image layers.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXImageView.AddImageLayer`
  - `NXImageView.RemoveImageLayer`
  - `NXImageView.ClearLayer`
- Verified source:
  - `Source/NXImage/NXImageView.h:112`
  - `Source/NXImage/NXImageView.h:822`
  - `Source/NXImage/NXImageView.h:836`
  - `Source/NXImage/NXImageView.h:841`
- Steps:
  - NXImageView를 호스트에 올린다.
  - NXImageLayer 파생 레이어를 만든다.
  - AddImageLayer(ref layer)로 연결한다.
  - 필요 시 RemoveImageLayer/ClearLayer로 정리한다.

## Required Facts
```yaml
workflow_family: image_view
output_shape: view_shell_or_hosted_control
required_symbols:
  - NXImageView.AddImageLayer
  - NXImageView.RemoveImageLayer
  - NXImageView.ClearLayer
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

- See also:
  - [nximageview-wpf-hosting.md](nximageview-wpf-hosting.md)
  - [xdl-imageview-wpf-examples.md](xdl-imageview-wpf-examples.md)

