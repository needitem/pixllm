---
title: Raster Composite Workflow
aliases:
  - Raster Composite Workflow
  - wf-raster-composite
  - wf raster composite
symbols:
  - XRSLoadFile
  - XDMBand
  - XDMComposite
  - XDMCompManager
  - NXImageLayerComposites
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Build grayscale or RGB composites from raster bands.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XRSLoadFile.GetBandAt`
  - `XDMComposite.SetBand`
  - `XDMCompManager.AddXDMComposite`
  - `XDMCompManager.RemoveXDMCompositeAll`
  - `NXImageLayerComposites.GetXDMCompManager`
  - `NXImageLayerComposites.ZoomFit`
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`
- Steps:
  - 파일에서 밴드 수를 확인한다.
  - 그레이면 1밴드, 컬러면 3밴드를 SetBand로 연결한다.
  - 관리자에 등록하고 ZoomFit으로 맞춘다.

## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XRSLoadFile.GetBandAt
  - XDMComposite.SetBand
  - XDMCompManager.AddXDMComposite
  - XDMCompManager.RemoveXDMCompositeAll
  - NXImageLayerComposites.GetXDMCompManager
  - NXImageLayerComposites.ZoomFit
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

- See also:
  - [imageview-xdm-display-workflow.md](imageview-xdm-display-workflow.md)
  - [xdl-imageview-wpf-examples.md](xdl-imageview-wpf-examples.md)
