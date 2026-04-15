---
title: Scene Editor IO Workflow
aliases:
  - Scene Editor IO Workflow
  - wf-scene-editor-io
  - wf scene editor io
symbols:
  - NXPlanetLayerSceneEditor
  - XScene
  - XscObj
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Create, open, merge, save, and inspect scenes through NXPlanetLayerSceneEditor.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXPlanetLayerSceneEditor.New`
  - `NXPlanetLayerSceneEditor.Clear`
  - `NXPlanetLayerSceneEditor.Open`
  - `NXPlanetLayerSceneEditor.Add`
  - `NXPlanetLayerSceneEditor.Save`
  - `NXPlanetLayerSceneEditor.GetScene`
  - `NXPlanetLayerSceneEditor.CreateNewOBJ`
- Verified source:
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:74`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:78`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:83`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:88`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:94`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:100`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:105`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:109`
  - `Source/NXDLscene/NXPlanetLayerSceneEditor.h:139`
- Steps:
  - scene editor layer를 planet view에 붙인다.
  - New/Open/Add/Clear로 내용을 제어한다.
  - GetScene과 CreateNewOBJ를 편집 흐름에 사용한다.

## Required Facts
```yaml
workflow_family: scene_or_vector
output_shape: focused_workflow_with_host_context
required_symbols:
  - NXPlanetLayerSceneEditor.New
  - NXPlanetLayerSceneEditor.Clear
  - NXPlanetLayerSceneEditor.Open
  - NXPlanetLayerSceneEditor.Add
  - NXPlanetLayerSceneEditor.Save
  - NXPlanetLayerSceneEditor.GetScene
  - NXPlanetLayerSceneEditor.CreateNewOBJ
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
