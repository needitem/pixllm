---
title: Pixoneer.NXDL.NSCENE.NXMilmapLayerSceneDisplay Methods
aliases:
  - NXMilmapLayerSceneDisplay Methods
  - Pixoneer.NXDL.NSCENE.NXMilmapLayerSceneDisplay
  - NXMilmapLayerSceneDisplay
symbols:
  - NXMilmapLayerSceneDisplay
  - Add
  - AttachTo
  - Clear
  - EnableAttrSet
  - GetLayerID
  - GetScene
  - HitTest
  - Initialize
  - New
  - Open
  - Save
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
- Type: `NXMilmapLayerSceneDisplay`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSCENE_NXMilmapLayerSceneDisplay.htm`
- Type declaration: `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:38`
- Method count: `11`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSCENE.NXMilmapLayerSceneDisplay
type_name: NXMilmapLayerSceneDisplay
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
- Description: 현재 화면에 scene 파일을 로딩하여 추가한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:81`, `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:87`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:90`, `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:98`

## AttachTo
- Description: 이 레이어를 군사 지도 뷰에 부착시킨다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:56`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:43`

## Clear
- Description: 레이어 안에 있는 모든 것을 지운다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:65`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:62`

## EnableAttrSet
- Description: 사용자가 설정한 속성의 사용여부를 설정한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:101`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:125`

## GetLayerID
- Description: 레이어의 고유 ID를 가져온다.(Overrides NXRenderLayerGetLayerID)
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:111`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:171`

## GetScene
- Description: 현재 표시되고 있는 Scene 객체를 확인한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:96`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:115`

## HitTest
- Description: 특정 좌표에 대해 객체의 hit-testing을 수행한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:108`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:133`

## Initialize
- Description: 엔진이 호출되면 자동으로 초기화 된다. (Overrides NXRenderLayerInitialize)
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:51`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:32`

## New
- Description: 새로운 scene을 생성한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:61`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:56`

## Open
- Description: 파일로부터 scene객체를 로딩하여 생성한다. 기존의 scene 객체가 있으면 새로운 scene으로 대체한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:70`, `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:75`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:68`, `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:81`

## Save
- Description: 현재 레이어의 scene 객체를 파일로 저장한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneDisplay.h:92`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneDisplay.cpp:107`
