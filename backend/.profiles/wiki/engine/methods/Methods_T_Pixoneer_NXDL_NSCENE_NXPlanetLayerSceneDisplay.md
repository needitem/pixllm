---
title: Pixoneer.NXDL.NSCENE.NXPlanetLayerSceneDisplay Methods
aliases:
  - NXPlanetLayerSceneDisplay Methods
  - Pixoneer.NXDL.NSCENE.NXPlanetLayerSceneDisplay
  - NXPlanetLayerSceneDisplay
symbols:
  - NXPlanetLayerSceneDisplay
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
- Type: `NXPlanetLayerSceneDisplay`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSCENE_NXPlanetLayerSceneDisplay.htm`
- Type declaration: `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:37`
- Method count: `11`

## Add
- Description: 현재 화면에 scene 파일을 로딩하여 추가한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:80`, `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:86`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:100`, `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:108`

## AttachTo
- Description: 이 레이어를 Planet 뷰에 부착시킨다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:55`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:52`

## Clear
- Description: 레이어 안에 있는 모든 것을 지운다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:64`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:72`

## EnableAttrSet
- Description: 사용자가 설정한 속성의 사용여부를 설정한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:103`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:146`

## GetLayerID
- Description: 레이어의 고유 ID를 가져온다.(Overrides NXRenderLayerGetLayerID)
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:129`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:227`

## GetScene
- Description: 현재 표시되고 있는 Scene 객체를 확인한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:95`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:125`

## HitTest
- Description: 특정 좌표에 대해 객체의 hit-testing을 수행하고 hit-testing된 모든 객체를 반환한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:110`, `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:117`, `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:123`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:154`, `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:173`, `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:186`

## Initialize
- Description: 엔진이 호출되면 자동으로 초기화 된다. (Overrides NXRenderLayerInitialize)
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:50`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:39`

## New
- Description: 새로운 scene을 생성한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:60`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:66`

## Open
- Description: 파일로부터 scene객체를 로딩하여 생성한다. 기존의 scene 객체가 있으면 새로운 scene으로 대체한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:69`, `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:74`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:78`, `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:91`

## Save
- Description: 현재 레이어의 scene 객체를 파일로 저장한다.
- Declaration: `Source/NXDLscene/NXPlanetLayerSceneDisplay.h:91`
- Implementation: `Source/NXDLscene/NXPlanetLayerSceneDisplay.cpp:117`
