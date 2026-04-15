---
title: Raster Grid Workflow
aliases:
  - Raster Grid Workflow
  - wf-raster-grid
  - wf raster grid
symbols:
  - XDMBand
  - XGrid
  - XColorTable
  - Xfn
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Read subsets and manipulate XGrid data directly.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XDMBand.ReadSubset`
  - `XGrid.Subset`
  - `XGrid.FlipVert`
  - `XGrid.FlipHorz`
  - `XGrid.GetValue`
  - `XGrid.SetValue`
  - `Xfn.MergeChannels`
  - `Xfn.SplitChannel`
  - `XColorTable.LoadColorTable`
  - `XColorTable.SetCLT`
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:971`
  - `Source/NXDL/NXDL.h:2525`
  - `Source/NXDL/NXDL.h:2530`
  - `Source/NXDL/NXDL.h:2535`
  - `Source/NXDL/NXDL.h:2591`
  - `Source/NXDL/NXDL.h:2680`
  - `Source/NXDL/NXDL.h:2812`
  - `Source/NXDL/NXDL.h:2824`
  - `Source/NXDL/NXDL.h:3778`
  - `Source/NXDL/NXDL.h:3788`
- Steps:
  - 필요 영역만 ReadSubset으로 읽는다.
  - XGrid에서 값 접근/뒤집기/부분 추출을 수행한다.
  - 필요 시 채널 merge/split과 컬러테이블을 적용한다.

## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XDMBand.ReadSubset
  - XGrid.Subset
  - XGrid.FlipVert
  - XGrid.FlipHorz
  - XGrid.GetValue
  - XGrid.SetValue
  - Xfn.MergeChannels
  - Xfn.SplitChannel
  - XColorTable.LoadColorTable
  - XColorTable.SetCLT
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
