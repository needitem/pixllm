---
title: Spatial Reference Workflow
aliases:
  - Spatial Reference Workflow
  - wf-coordinate-sr
  - wf coordinate sr
symbols:
  - XSpatialReference
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Create and inspect spatial references before transforming points.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XSpatialReference.SetWellKnownGeogCS`
  - `XSpatialReference.IsGeographic`
  - `XSpatialReference.IsProjected`
  - `XSpatialReference.IsUTM`
  - `XSpatialReference.GetUTMZone`
  - `XSpatialReference.IsSame`
  - `XSpatialReference.GetAreaOfUse`
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:152`
  - `Source/NXDLcc/NXDLcc.h:156`
  - `Source/NXDLcc/NXDLcc.h:170`
  - `Source/NXDLcc/NXDLcc.h:183`
  - `Source/NXDLcc/NXDLcc.h:194`
  - `Source/NXDLcc/NXDLcc.h:198`
  - `Source/NXDLcc/NXDLcc.h:213`
- Steps:
  - 입력/출력 SR을 먼저 만든다.
  - 좌표계 타입과 UTM 여부를 확인한다.
  - 필요 시 적용 범위를 확인한다.

## Required Facts
```yaml
workflow_family: coordinate
output_shape: focused_snippet_or_helper
required_symbols:
  - XSpatialReference.SetWellKnownGeogCS
  - XSpatialReference.IsGeographic
  - XSpatialReference.IsProjected
  - XSpatialReference.IsUTM
  - XSpatialReference.GetUTMZone
  - XSpatialReference.IsSame
  - XSpatialReference.GetAreaOfUse
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
