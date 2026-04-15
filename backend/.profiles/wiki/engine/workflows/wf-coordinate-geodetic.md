---
title: Geodetic Utility Workflow
aliases:
  - Geodetic Utility Workflow
  - wf-coordinate-geodetic
  - wf coordinate geodetic
symbols:
  - Xcc
  - Xfn
  - XGeoPoint
  - XAngle
  - XVertex3d
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Use geodetic helper functions for distance, angle, area, and geo/ecr conversion.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `Xcc.CalcGeodeticDistance`
  - `Xcc.CalcGeodeticAngle`
  - `Xcc.CalcGeodeticArea`
  - `Xcc.ConvPixelSize`
  - `Xfn.GeoToEcr`
  - `Xfn.EcrToGeo`
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`
- Steps:
  - 물리 질문의 종류를 먼저 정한다.
  - XAngle/XGeoPoint 기준으로 입력을 유지한다.
  - 필요한 지오데틱 유틸을 호출한다.

## Required Facts
```yaml
workflow_family: coordinate
output_shape: focused_snippet_or_helper
required_symbols:
  - Xcc.CalcGeodeticDistance
  - Xcc.CalcGeodeticAngle
  - Xcc.CalcGeodeticArea
  - Xcc.ConvPixelSize
  - Xfn.GeoToEcr
  - Xfn.EcrToGeo
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
