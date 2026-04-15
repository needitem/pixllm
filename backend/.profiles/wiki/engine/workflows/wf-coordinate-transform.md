---
title: Coordinate Transform Workflow
aliases:
  - Coordinate Transform Workflow
  - wf-coordinate-transform
  - wf coordinate transform
symbols:
  - XCoordinateTransformation
  - XSpatialReference
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Build a reusable coordinate transformation from two SRs.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XCoordinateTransformation.CreateCoordinateTransform`
  - `XCoordinateTransformation.TransformPt`
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:265`
  - `Source/NXDLcc/NXDLcc.h:269`
  - `Source/NXDLcc/NXDLcc.h:291`
  - `Source/NXDLcc/NXDLcc.h:301`
  - `Source/NXDLcc/NXDLcc.h:309`
- Steps:
  - 입력/출력 SR을 준비한다.
  - 변환기를 생성한다.
  - TransformPt를 반복 호출한다.

## Required Facts
```yaml
workflow_family: coordinate
output_shape: focused_snippet_or_helper
required_symbols:
  - XCoordinateTransformation.CreateCoordinateTransform
  - XCoordinateTransformation.TransformPt
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```

## Output Guidance
- Explanation requests: summarize the ordered call chain, prerequisites, and verified source anchors.
- Code/sample requests: prefer a focused helper, method, or minimal snippet unless the user explicitly asks for a full app shell.
- Keep the sample scoped to this workflow and do not mix neighboring subsystems unless the user explicitly asks for them.

## Common Wrong Patterns
- Do not invent helper methods or short overloads outside the verified symbol set above.
- Do not convert verified methods into properties, or properties into methods, without source proof.
- Do not guess `ref`/`out`, enum literals, or return types from naming alone.
- Do not skip prerequisites implied by the ordered call chain in this workflow.
