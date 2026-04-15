---
title: Image Processing Workflow
aliases:
  - Image Processing Workflow
  - wf-image-processing
  - wf image processing
symbols:
  - NXImageLayer
  - eImageProcessingFilter
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Apply shader or filter processing to NXImageLayer.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXImageLayer.EnableShaderAlgorithm`
  - `NXImageLayer.SetShaderAlgorithm`
  - `NXImageLayer.GenShaderCodeCBS`
  - `NXImageLayer.GenShaderCodeHDR`
  - `NXImageLayer.GenShaderCodeEdge`
  - `NXImageLayer.GenShaderCodeBasso`
  - `NXImageLayer.GenShaderCodeAverage`
  - `NXImageLayer.GenShaderCodeMedian`
  - `NXImageLayer.SetFilterType`
  - `NXImageLayer.SetFilterSize`
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`
- Steps:
  - shader 경로인지 filter 경로인지 먼저 정한다.
  - EnableShaderAlgorithm(true)를 켠다.
  - 질문한 GenShaderCode 또는 Filter API를 적용한다.
  - 다시 그린다.

## Required Facts
```yaml
workflow_family: image_view
output_shape: view_shell_or_hosted_control
required_symbols:
  - NXImageLayer.EnableShaderAlgorithm
  - NXImageLayer.SetShaderAlgorithm
  - NXImageLayer.GenShaderCodeCBS
  - NXImageLayer.GenShaderCodeHDR
  - NXImageLayer.GenShaderCodeEdge
  - NXImageLayer.GenShaderCodeBasso
  - NXImageLayer.GenShaderCodeAverage
  - NXImageLayer.GenShaderCodeMedian
  - NXImageLayer.SetFilterType
  - NXImageLayer.SetFilterSize
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
