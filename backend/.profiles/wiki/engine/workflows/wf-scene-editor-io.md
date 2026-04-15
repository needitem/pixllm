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
output_shape: workflow_bound_to_host_context
required_symbols:
  - NXPlanetLayerSceneEditor.New
  - NXPlanetLayerSceneEditor.Clear
  - NXPlanetLayerSceneEditor.Open
  - NXPlanetLayerSceneEditor.Add
  - NXPlanetLayerSceneEditor.Save
  - NXPlanetLayerSceneEditor.GetScene
  - NXPlanetLayerSceneEditor.CreateNewOBJ
required_facts:
  - symbol: NXPlanetLayerSceneEditor.New
    declaration: 'bool New	();'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:74'
  - symbol: NXPlanetLayerSceneEditor.Clear
    declaration: 'bool Clear	();'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:78'
  - symbol: NXPlanetLayerSceneEditor.Open
    declaration_candidates:
      - declaration: 'bool Open	(String^ strFile);'
        source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:83'
      - declaration: 'bool Open	(XScene^ pScene);'
        source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:88'
  - symbol: NXPlanetLayerSceneEditor.Add
    declaration_candidates:
      - declaration: 'bool Add	(String^ strFile, bool bMerge);'
        source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:94'
      - declaration: 'bool Add	(XScene^ pScene, bool bMerge);'
        source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:100'
  - symbol: NXPlanetLayerSceneEditor.Save
    declaration: 'bool Save	(String^ strFile);'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:105'
  - symbol: NXPlanetLayerSceneEditor.GetScene
    declaration: 'XScene^		GetScene();'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:109'
  - symbol: NXPlanetLayerSceneEditor.CreateNewOBJ
    declaration: 'XscObj^		CreateNewOBJ(String^ strType);'
    source: 'Source/NXDLscene/NXPlanetLayerSceneEditor.h:139'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
