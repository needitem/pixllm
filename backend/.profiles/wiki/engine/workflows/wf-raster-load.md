---
title: Raster Load Workflow
aliases:
  - Raster Load Workflow
  - wf-raster-load
  - wf raster load
symbols:
  - XRasterIO
  - XVectorIO
  - XRawDataParam
  - XRSLoadFile
  - XvcBase
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Initialize XRasterIO/XVectorIO and load data.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XRasterIO.Initialize`
  - `XRasterIO.LoadFile`
  - `XRasterIO.GetSubDatasets`
  - `XRasterIO.LoadRawFile`
  - `XRasterIO.GetFileInfo`
  - `XVectorIO.Initialize`
  - `XVectorIO.LoadFile`
  - `XVectorIO.GetFileInfo`
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
- Steps:
  - IO 매니저를 생성하고 Initialize를 호출한다.
  - LoadFile 또는 LoadRawFile 경로를 고른다.
  - 멀티서브데이터셋이면 GetSubDatasets를 먼저 본다.
  - 벡터면 XVectorIO 경로로 분기한다.

## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XRasterIO.Initialize
  - XRasterIO.LoadFile
  - XRasterIO.GetSubDatasets
  - XRasterIO.LoadRawFile
  - XRasterIO.GetFileInfo
  - XVectorIO.Initialize
  - XVectorIO.LoadFile
  - XVectorIO.GetFileInfo
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
