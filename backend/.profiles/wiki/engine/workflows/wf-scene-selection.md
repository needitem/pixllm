---
title: Scene Selection Workflow
aliases:
  - Scene Selection Workflow
  - wf-scene-selection
  - wf scene selection
symbols:
  - NXPlanetLayerSceneEditor
  - XscObj
  - XHitFlag
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Hit-test, select, and finish scene editing.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXPlanetLayerSceneEditor.HitTest`
  - `NXPlanetLayerSceneEditor.SelectNone`
  - `NXPlanetLayerSceneEditor.SelectAll`
  - `NXPlanetLayerSceneEditor.SelectObject`
  - `NXPlanetLayerSceneEditor.EditObjectEnd`
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:121`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:128`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:134`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:143`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:147`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:153`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:158`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:163`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:170`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:174`
- Steps:
  - HitTest로 대상을 찾는다.
  - SelectNone/All/Object로 선택 상태를 바꾼다.
  - 편집 종료 시 EditObjectEnd를 호출한다.

## Required Facts
```yaml
workflow_family: scene_or_vector
output_shape: focused_workflow_with_host_context
required_symbols:
  - NXPlanetLayerSceneEditor.HitTest
  - NXPlanetLayerSceneEditor.SelectNone
  - NXPlanetLayerSceneEditor.SelectAll
  - NXPlanetLayerSceneEditor.SelectObject
  - NXPlanetLayerSceneEditor.EditObjectEnd
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
