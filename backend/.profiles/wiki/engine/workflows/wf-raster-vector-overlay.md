---
title: Raster Vector Overlay Workflow
aliases:
  - Raster Vector Overlay Workflow
  - wf-raster-vector-overlay
  - wf raster vector overlay
symbols:
  - XVectorIO
  - XvcBase
  - NXImageView
  - NXImageLayerVectorDisplay
  - NXImageLayerVectorEditor
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Load vector data and overlay it on raster/image views.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XVectorIO.Initialize`
  - `XVectorIO.GetFileInfo`
  - `XVectorIO.LoadFile`
  - `NXImageView.AddImageLayer`
- Verified source:
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
  - `Source/NXImage/NXImageView.h:836`
- Steps:
  - 벡터 IO를 초기화한다.
  - 필요 시 메타정보를 읽는다.
  - 벡터 파일을 로드하고 벡터 레이어를 뷰에 붙인다.

## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XVectorIO.Initialize
  - XVectorIO.GetFileInfo
  - XVectorIO.LoadFile
  - NXImageView.AddImageLayer
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
