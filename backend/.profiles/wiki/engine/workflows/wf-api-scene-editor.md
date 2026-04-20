---
title: Scene Editor API Workflow
aliases:
  - scene editor api
  - planet scene editor
  - scene object selection
  - scene save open
  - scene 파일을 새로 만드는 방법
  - scene 파일을 열고 저장하는 방법
  - scene 객체를 새로 생성하는 방법
  - scene에서 hit test로 객체를 찾는 방법
  - scene 객체를 선택하는 방법
  - scene 선택을 모두 해제하는 방법
  - scene 객체 편집을 종료하는 방법
  - scene 파일을 병합하거나 add 하는 방법
  - scene object hit test
  - scene object select none
  - scene object select all
  - scene object edit end
symbols:
  - NXPlanetLayerSceneEditor
  - XScene
  - XscObj
  - XHitFlag
tags:
  - engine
  - workflow
  - api
  - scene
---

# Overview
- Goal: create/open/save scenes and select scene objects through `NXPlanetLayerSceneEditor`.
- This workflow merges scene IO and selection into one API family page.
- Prefer this family when the question explicitly says `scene`, `scene 파일`, `scene 객체`, or scene-object selection lifecycle.
- If the question names `scene object` selection, hit testing, select none/all, or scene-file new/open/save/add/merge, prefer this family over plain `Editor`.

## Knowledge Bundle
```yaml
concept_terms:
- scene object
- object io
- scene graph
routing_hints:
- all_of: [scene, 선택]
- all_of: [scene, hit test]
- all_of: [scene, 편집을 종료]
- all_of: [scene, 객체]
bundle_pages:
- path: pages/howtos/scene-editor-object-io.md
  relation: family_howto
- path: pages/concepts/editor-and-scene-object-lifecycle.md
  relation: family_concept
- path: workflows/wf-api-editor.md
  relation: dependency_workflow
- path: pages/sources/nxdlscene.md
  relation: source_summary
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-20T00:52:13Z`.
- Resolved required symbols: `12/12`
- Linked modules:
  - `NXDLscene`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Required Facts
```yaml
workflow_family: api_scene_editor
output_shape: workflow_bound_to_host_context
required_symbols:
  - NXPlanetLayerSceneEditor.New
  - NXPlanetLayerSceneEditor.Clear
  - NXPlanetLayerSceneEditor.Open
  - NXPlanetLayerSceneEditor.Add
  - NXPlanetLayerSceneEditor.Save
  - NXPlanetLayerSceneEditor.GetScene
  - NXPlanetLayerSceneEditor.CreateNewOBJ
  - NXPlanetLayerSceneEditor.HitTest
  - NXPlanetLayerSceneEditor.SelectNone
  - NXPlanetLayerSceneEditor.SelectAll
  - NXPlanetLayerSceneEditor.SelectObject
  - NXPlanetLayerSceneEditor.EditObjectEnd
required_facts:
  - symbol: NXPlanetLayerSceneEditor.New
    declaration: 'bool New ();'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:74'
  - symbol: NXPlanetLayerSceneEditor.Open
    declaration: 'bool Open (String^ strFile);'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:83'
  - symbol: NXPlanetLayerSceneEditor.Save
    declaration: 'bool Save (String^ strFile);'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:105'
  - symbol: NXPlanetLayerSceneEditor.GetScene
    declaration: 'XScene^ GetScene();'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:109'
  - symbol: NXPlanetLayerSceneEditor.CreateNewOBJ
    declaration: 'XscObj^ CreateNewOBJ(String^ strType);'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:139'
  - symbol: NXPlanetLayerSceneEditor.HitTest
    declaration: 'XscObj^ HitTest (XVertex3d^ vWorld, double dPixelSize, XHitFlag^% hit);'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:121'
  - symbol: NXPlanetLayerSceneEditor.SelectObject
    declaration: 'bool SelectObject(XscObj^ pObj, bool bSingleSelect);'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:153'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```

