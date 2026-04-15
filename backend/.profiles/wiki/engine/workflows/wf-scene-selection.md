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
output_shape: workflow_bound_to_host_context
required_symbols:
  - NXPlanetLayerSceneEditor.HitTest
  - NXPlanetLayerSceneEditor.SelectNone
  - NXPlanetLayerSceneEditor.SelectAll
  - NXPlanetLayerSceneEditor.SelectObject
  - NXPlanetLayerSceneEditor.EditObjectEnd
required_facts:
  - symbol: NXPlanetLayerSceneEditor.HitTest
    declaration_candidates:
      - declaration: 'XscObj^		HitTest	(XVertex3d^ vWorld, double dPixelSize, XHitFlag^% hit);'
        source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:121'
      - declaration: 'bool		HitTest	(XVertex3d^ vLL, XVertex3d^ vUR, [OutAttribute] ArrayList^% outArray);'
        source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:128'
      - declaration: 'bool		HitTest	(XVertex3d^ vWorld, [OutAttribute] ArrayList^% outArray);'
        source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:134'
  - symbol: NXPlanetLayerSceneEditor.SelectNone
    declaration: 'void		SelectNone	();'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:143'
  - symbol: NXPlanetLayerSceneEditor.SelectAll
    declaration: 'bool		SelectAll	();'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:147'
  - symbol: NXPlanetLayerSceneEditor.SelectObject
    declaration_candidates:
      - declaration: 'bool		SelectObject(XscObj^ pObj, bool bSingleSelect);'
        source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:153'
      - declaration: 'bool		SelectObject(ArrayList^ objs);'
        source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:158'
      - declaration: 'bool		SelectObject(int nID);'
        source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:163'
  - symbol: NXPlanetLayerSceneEditor.EditObjectEnd
    declaration: 'bool		EditObjectEnd();'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:174'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
