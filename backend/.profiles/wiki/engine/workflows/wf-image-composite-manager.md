---
title: Image Composite Manager Workflow
aliases:
  - Image Composite Manager Workflow
  - wf-image-composite-manager
  - wf image composite manager
symbols:
  - NXImageLayerComposites
  - XDMCompManager
  - XDMComposite
  - XDMBand
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Manage composites through NXImageLayerComposites and XDMCompManager.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXImageLayerComposites.GetXDMCompManager`
  - `NXImageLayerComposites.Lock`
  - `NXImageLayerComposites.UnLock`
  - `NXImageLayerComposites.EnableCache`
  - `NXImageLayerComposites.EnableThread`
  - `NXImageLayerComposites.SetEnableUpdateAtEnd`
  - `NXImageLayerComposites.InvalidateCache`
  - `NXImageLayerComposites.ReadPixelValues`
  - `NXImageLayerComposites.HitTest`
  - `XDMCompManager.AddXDMComposite`
  - `XDMCompManager.RemoveXDMCompositeAll`
  - `XDMComposite.SetBand`
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
- Steps:
  - GetXDMCompManager로 관리자를 얻는다.
  - Lock/UnLock 사이에서 Composite를 갱신한다.
  - 캐시/스레드/inspect API를 필요한 만큼 쓴다.
  - ZoomFit 또는 Invalidate로 반영한다.

## Required Facts
```yaml
workflow_family: image_view
output_shape: view_shell_or_hosted_control
required_symbols:
  - NXImageLayerComposites.GetXDMCompManager
  - NXImageLayerComposites.Lock
  - NXImageLayerComposites.UnLock
  - NXImageLayerComposites.EnableCache
  - NXImageLayerComposites.EnableThread
  - NXImageLayerComposites.SetEnableUpdateAtEnd
  - NXImageLayerComposites.InvalidateCache
  - NXImageLayerComposites.ReadPixelValues
  - NXImageLayerComposites.HitTest
  - XDMCompManager.AddXDMComposite
  - XDMCompManager.RemoveXDMCompositeAll
  - XDMComposite.SetBand
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```

## Output Guidance
- Explanation requests: summarize the host control, layer attachment order, and the exact display/update path.
- Code/sample requests: include the host/view/layer wiring first, then the data-load/composite path.
- If the user asks for WPF, include the XAML shell and code-behind instead of returning only a single `.cs` file.

## Common Wrong Patterns
- Do not invent helper methods or short overloads outside the verified symbol set above.
- Do not convert verified methods into properties, or properties into methods, without source proof.
- Do not guess `ref`/`out`, enum literals, or return types from naming alone.
- Do not skip prerequisites implied by the ordered call chain in this workflow.
- Do not return only an isolated view call when the actual workflow depends on layer attachment and display/update steps.
