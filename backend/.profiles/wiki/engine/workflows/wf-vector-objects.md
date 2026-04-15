---
title: Vector Objects Workflow
aliases:
  - Vector Objects Workflow
  - wf-vector-objects
  - wf vector objects
symbols:
  - XvcObj
  - XvcPoint
  - XvcLine
  - XvcPolyline
  - XvcPolygon
  - XvcLayer
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Create vector geometry, inspect attributes, and hit-test vector layers.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XvcObj.GetPropertyNameAt`
  - `XvcObj.GetPropertyValueAt`
  - `XvcPoint.Add`
  - `XvcLine.Add`
  - `XvcPolyline.Add`
  - `XvcPolygon.Add`
  - `XvcLayer.HitTest`
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`
- Steps:
  - 객체를 로드하거나 생성한다.
  - 속성은 property API로 읽는다.
  - 지오메트리는 Add 계열로 구성한다.
  - 선택/탐색은 HitTest로 처리한다.

## Required Facts
```yaml
workflow_family: scene_or_vector
output_shape: focused_workflow_with_host_context
required_symbols:
  - XvcObj.GetPropertyNameAt
  - XvcObj.GetPropertyValueAt
  - XvcPoint.Add
  - XvcLine.Add
  - XvcPolyline.Add
  - XvcPolygon.Add
  - XvcLayer.HitTest
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```

## Output Guidance
- Explanation requests: summarize object creation, edit/display ownership, and save/load or hit-test order.
- Code/sample requests: include the controlling layer/view context before the object-edit sequence.
- If the workflow is UI-driven, do not return isolated API calls without the layer or view context that owns them.

## Common Wrong Patterns
- Do not invent helper methods or short overloads outside the verified symbol set above.
- Do not convert verified methods into properties, or properties into methods, without source proof.
- Do not guess `ref`/`out`, enum literals, or return types from naming alone.
- Do not skip prerequisites implied by the ordered call chain in this workflow.
