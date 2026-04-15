---
title: Raster Enhance Workflow
aliases:
  - Raster Enhance Workflow
  - wf-raster-enhance
  - wf raster enhance
symbols:
  - XDMComposite
  - eCompCutType
  - eCompStretchCoverage
  - eCompStretchType
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Tune cut and stretch parameters for display quality.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XDMComposite.SetCutType`
  - `XDMComposite.SetStretchCoverage`
  - `XDMComposite.SetStretchType`
  - `XDMComposite.SetCutMin`
  - `XDMComposite.SetCutMax`
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`
- Steps:
  - 기존 Composite를 유지한다.
  - cut/stretch 설정을 조정한다.
  - 수동 min/max는 마지막에만 사용한다.

## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XDMComposite.SetCutType
  - XDMComposite.SetStretchCoverage
  - XDMComposite.SetStretchType
  - XDMComposite.SetCutMin
  - XDMComposite.SetCutMax
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
