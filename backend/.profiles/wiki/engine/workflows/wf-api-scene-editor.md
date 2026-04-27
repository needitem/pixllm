---
title: Scene Editor API Workflow
description: Create, open, save, and select scene objects through the scene editor family.
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
- For the current wiki routing, use this family when the question explicitly says `scene`, `scene 파일`, `scene 객체`, or scene-object selection lifecycle.
- For the current wiki routing, `scene object` selection, hit testing, select none/all, and scene-file new/open/save/add/merge stay in this family rather than plain `Editor`.

## Primary Usage Buckets
- `scene 파일`: `New`, `Open`, `Add`, `Save`, `Clear`
- `scene 객체`: `CreateNewOBJ`, `GetScene`
- `scene 선택`: `HitTest`, `SelectObject`, `SelectNone`, `SelectAll`
- `편집 종료`: `EditObjectEnd`

## Practical Answer Shape
- `scene 파일 생성/열기/저장`: 파일 lifecycle과 object lifecycle을 분리해서 설명합니다.
- `scene 객체 생성`: `CreateNewOBJ`와 이후 selection/edit 흐름을 같이 답합니다.
- `scene 선택`: `HitTest` -> `SelectObject` 또는 `SelectNone/All` 순서로 설명합니다.
- `scene 편집 종료`: plain editor 종료와 구분해서 `EditObjectEnd`를 우선 제시합니다.


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

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
- Auto-generated from raw source ingest at `2026-04-27T01:07:34Z`.
- Resolved required symbols: `12/12`
- Linked modules:
  - `NXDLscene`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
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
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```


