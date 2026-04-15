---
title: Raster ROI Signature Workflow
aliases:
  - Raster ROI Signature Workflow
  - wf-raster-roi-sig
  - wf raster roi sig
symbols:
  - XROI
  - XSIG
  - XSIGSet
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Compute ROI and signature statistics.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XROI.CalcStatistics`
  - `XROI.GetMean`
  - `XROI.GetStd`
  - `XROI.GetHistogram`
  - `XROI.GetCorrelation`
  - `XSIG.AddROI`
  - `XSIG.CalcStatistics`
  - `XSIGSet.AddSIG`
  - `XSIGSet.LoadSIGSet`
  - `XSIGSet.SaveSIGSet`
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:288`
  - `Source/NXDLrs/NXDLrs.h:293`
  - `Source/NXDLrs/NXDLrs.h:311`
  - `Source/NXDLrs/NXDLrs.h:317`
  - `Source/NXDLrs/NXDLrs.h:346`
  - `Source/NXDLrs/NXDLrs.h:378`
  - `Source/NXDLrs/NXDLrs.h:401`
  - `Source/NXDLrs/NXDLrs.h:481`
  - `Source/NXDLrs/NXDLrs.h:502`
  - `Source/NXDLrs/NXDLrs.h:507`
  - `Source/NXDLrs/NXDLrs.h:513`
- Steps:
  - ROI를 정의한다.
  - CalcStatistics를 먼저 수행한다.
  - 이후 mean/std/histogram/correlation 또는 SIG 저장/불러오기를 수행한다.

## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XROI.CalcStatistics
  - XROI.GetMean
  - XROI.GetStd
  - XROI.GetHistogram
  - XROI.GetCorrelation
  - XSIG.AddROI
  - XSIG.CalcStatistics
  - XSIGSet.AddSIG
  - XSIGSet.LoadSIGSet
  - XSIGSet.SaveSIGSet
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
