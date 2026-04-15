---
title: Pixoneer.NXDL.NSCENE.NXPlanetLayerSceneEditor Methods
aliases:
  - NXPlanetLayerSceneEditor Methods
  - Pixoneer.NXDL.NSCENE.NXPlanetLayerSceneEditor
  - NXPlanetLayerSceneEditor
symbols:
  - NXPlanetLayerSceneEditor
  - Add
  - AttachTo
  - Clear
  - CreateNewOBJ
  - EditObjectEnd
  - EnableAttrSet
  - GetLayerID
  - GetScene
  - HitTest
  - Initialize
  - New
  - Open
  - Save
  - SelectAll
  - SelectNone
  - SelectObject
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nscene
---

# Overview
- Namespace: `Pixoneer.NXDL.NSCENE`
- Type: `NXPlanetLayerSceneEditor`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSCENE_NXPlanetLayerSceneEditor.htm`
- Type declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:50`
- Method count: `16`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSCENE.NXPlanetLayerSceneEditor
type_name: NXPlanetLayerSceneEditor
namespace: Pixoneer.NXDL.NSCENE
method_section_prefix: "## "
verification_rules:
  - treat_declaration_lines_as_symbol_existence_evidence
  - treat_implementation_lines_as_source_anchor_evidence
  - use_this_page_only_after_a_workflow_or_type_hint_narrows_scope
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page only as a verification layer after a workflow or explicit type hint identifies the target type.
- Cross-check declaration and implementation lines when overloads, properties, or call shapes matter.
- Do not synthesize end-to-end usage answers from this page alone.
## Add
- Description: 현재 화면에 scene 파일로부터 로딩하여 추가한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:94`, `Source/NXDLscene/NXPlanetLayerSceneEditor.h:100`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:127`, `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:135`

## AttachTo
- Description: 이 레이어를 Planet 뷰에 부착시킨다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:68`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:77`

## Clear
- Description: 레이어 안에 있는 모든것을 지운다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:78`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:98`

## CreateNewOBJ
- Description: 객체 종류에 따라 scene 객체를 생성한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:139`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:216`

## EditObjectEnd
- Description: 객체 편집을 종료하도록 한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:174`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:277`

## EnableAttrSet
- Description: 사용자가 설정한 속성의 사용여부를 설정한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:114`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:161`

## GetLayerID
- Description: 레이어의 고유 ID를 가져온다.(Overrides NXRenderLayerGetLayerID)
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:186`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:355`

## GetScene
- Description: 현재 표시되고 있는 Scene 객체를 확인한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:109`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:152`

## HitTest
- Description: 특정 좌표에 대해 객체의 hit-testing을 수행하고 hit-testing된 모든 객체를 반환한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:121`, `Source/NXDLscene/NXPlanetLayerSceneEditor.h:128`, `Source/NXDLscene/NXPlanetLayerSceneEditor.h:134`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:169`, `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:188`, `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:202`

## Initialize
- Description: 엔진이 호출되면 자동으로 초기화 된다. (Overrides NXRenderLayerInitialize)
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:63`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:57`

## New
- Description: 새로운 scene을 생성한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:74`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:91`

## Open
- Description: 파일로부터 senescence 불러 온다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:83`, `Source/NXDLscene/NXPlanetLayerSceneEditor.h:88`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:105`, `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:118`

## Save
- Description: 현재 레이어의 scene 객체를 파일로 저장한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:105`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:144`

## SelectAll
- Description: 모든 객체를 선택한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:147`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:231`

## SelectNone
- Description: 선택사항을 모두 해제하고 아무것도 선택하지 않은 것으로 설정한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:143`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:225`

## SelectObject
- Description: 대상 객체를 선택한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneEditor.h:153`, `Source/NXDLscene/NXPlanetLayerSceneEditor.h:158`, `Source/NXDLscene/NXPlanetLayerSceneEditor.h:163`, `Source/NXDLscene/NXPlanetLayerSceneEditor.h:170`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:238`, `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:244`, `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:258`, `Source/NXDLscene/NXPlanetLayerSceneEditor.cpp:266`
