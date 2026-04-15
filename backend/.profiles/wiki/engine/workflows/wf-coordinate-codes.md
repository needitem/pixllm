---
title: Coordinate Code Workflow
aliases:
  - Coordinate Code Workflow
  - wf-coordinate-codes
  - wf coordinate codes
symbols:
  - Xcc
  - XAngle
  - XVertex2d
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Convert between WGS84, UTM, MGRS, and GEOREF.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `Xcc.WGP2UTM`
  - `Xcc.UTM2WGP`
  - `Xcc.WGP2MGRS`
  - `Xcc.MGRS2UTM`
  - `Xcc.MGRS2WGP`
  - `Xcc.WGP2GEOREF`
  - `Xcc.GEOREF2WGP`
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:340`
  - `Source/NXDLcc/NXDLcc.h:344`
  - `Source/NXDLcc/NXDLcc.h:370`
  - `Source/NXDLcc/NXDLcc.h:397`
  - `Source/NXDLcc/NXDLcc.h:419`
  - `Source/NXDLcc/NXDLcc.h:464`
  - `Source/NXDLcc/NXDLcc.h:522`
  - `Source/NXDLcc/NXDLcc.h:541`
  - `Source/NXDLcc/NXDLcc.h:587`
  - `Source/NXDLcc/NXDLcc.h:605`
- Steps:
  - WGS84 lon/lat 입력을 준비한다.
  - 대상 코드 체계를 고른다.
  - 필요 시 역변환 함수를 사용한다.

## Required Facts
```yaml
workflow_family: coordinate
output_shape: focused_snippet_or_helper
required_symbols:
  - Xcc.WGP2UTM
  - Xcc.UTM2WGP
  - Xcc.WGP2MGRS
  - Xcc.MGRS2UTM
  - Xcc.MGRS2WGP
  - Xcc.WGP2GEOREF
  - Xcc.GEOREF2WGP
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
