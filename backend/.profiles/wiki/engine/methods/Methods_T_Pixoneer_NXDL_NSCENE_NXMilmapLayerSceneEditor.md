---
title: Pixoneer.NXDL.NSCENE.NXMilmapLayerSceneEditor Methods
aliases:
  - NXMilmapLayerSceneEditor Methods
  - Pixoneer.NXDL.NSCENE.NXMilmapLayerSceneEditor
  - NXMilmapLayerSceneEditor
symbols:
  - NXMilmapLayerSceneEditor
  - Add
  - AttachTo
  - Clear
  - CreateNewOBJ
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
- Type: `NXMilmapLayerSceneEditor`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSCENE_NXMilmapLayerSceneEditor.htm`
- Type declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:35`
- Method count: `15`

## Add
- Description: 현재 화면에 scene 파일로부터 로딩하여 추가한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:123`, `Source/NXDLscene/NXMilmapLayerSceneEditor.h:129`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:112`, `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:120`

## AttachTo
- Description: 이 레이어를 군사 지도 뷰에 부착시킨다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:98`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:62`

## Clear
- Description: 레이어 안에 있는 모든것을 지운다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:107`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:83`

## CreateNewOBJ
- Description: 종류에 따라 scene 객체를 생성한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:155`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:175`

## EnableAttrSet
- Description: 사용자가 설정한 속성의 사용여부를 설정한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:143`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:147`

## GetLayerID
- Description: 레이어의 고유 ID를 가져온다.(Overrides NXRenderLayerGetLayerID)
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:184`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:248`

## GetScene
- Description: 현재 표시되고 있는 Scene 객체를 확인한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:138`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:137`

## HitTest
- Description: 지정된 점에서 객체의 hit-testing 을 수행한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:150`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:155`

## Initialize
- Description: 엔진이 호출 되면 자동으로 초기화 된다. (Overrides NXRenderLayerInitialize)
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:93`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:46`

## New
- Description: 새로운 scene을 생성한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:103`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:76`

## Open
- Description: 파일로부터 scene객체를 불러 온다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:112`, `Source/NXDLscene/NXMilmapLayerSceneEditor.h:117`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:90`, `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:103`

## Save
- Description: 현재 레이어의 scene 객체를 파일로 저장한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:134`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:129`

## SelectAll
- Description: 모든 객체를 선택한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:163`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:190`

## SelectNone
- Description: 선택사항을 모두 해제하고 아무것도 선택하지 않은 것으로 설정한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:159`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:184`

## SelectObject
- Description: 대상 객체를 선택한다.
- Declaration: `Source/NXDLscene/NXMilmapLayerSceneEditor.h:169`, `Source/NXDLscene/NXMilmapLayerSceneEditor.h:174`, `Source/NXDLscene/NXMilmapLayerSceneEditor.h:181`
- Implementation: `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:197`, `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:203`, `Source/NXDLscene/NXMilmapLayerSceneEditor.cpp:217`
