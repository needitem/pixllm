---
title: Pixoneer.NXDL.NXPlanet.NXPlanetLayerVectorEditor Methods
aliases:
  - NXPlanetLayerVectorEditor Methods
  - Pixoneer.NXDL.NXPlanet.NXPlanetLayerVectorEditor
  - NXPlanetLayerVectorEditor
symbols:
  - NXPlanetLayerVectorEditor
  - ClearLayer
  - CreateNewOBJ
  - Delete
  - GetEditBase
  - GetLayerDisplayOrder
  - GetLayerID
  - GetSelectedObj
  - HitTest
  - Initialize
  - Lock
  - Modify
  - SelectNone
  - SelectObject
  - SetEditBase
  - SetLayerDisplayOrder
  - UnLock
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nxplanet
---

# Overview
- Namespace: `Pixoneer.NXDL.NXPlanet`
- Type: `NXPlanetLayerVectorEditor`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXPlanet_NXPlanetLayerVectorEditor.htm`
- Type declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:23`
- Method count: `16`

## ClearLayer
- Description: 벡터 레이어에 도시된 객체를 모두 삭제한다. Undo/Redo command 도 모두 삭제된다.
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:198`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:101`

## CreateNewOBJ
- Description: 객체 형식과 정점 배열을 이용하여 새로운 객체를 생성한다. Ellipse, MeasureAngle, MeasureArea, MeasurePoint, MeasureDist, Point, Polygon, Polyline, Rectangle, Symbol, Text 객체 형식 지원
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:139`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:149`

## Delete
- Description: 선택된 객체를 삭제한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:51`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:254`

## GetEditBase
- Description: 편집을 위한 베이스 객체을 가져온다.(XvcBase는 하나 이상의 레이어로 구성되며, 레이어(XvcLayer)는 여러 개의 객체로 포함한다.)
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:161`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:84`

## GetLayerDisplayOrder
- Description: 편집 베이스(EditBase)의 레이어(XvcLayer)들의 도시 순서 배열을 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:202`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:107`

## GetLayerID
- Description: 레이어의 고유 ID를 가져온다.(Overrides NXRenderLayerGetLayerID)
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:254`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:78`

## GetSelectedObj
- Description: 현재 선택된 객체를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:149`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:196`

## HitTest
- Description: 특정 위치에 해당 객체의 hit-testing을 수행한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:145`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:174`

## Initialize
- Description: 내부 초기화 함수이다. 이것은 NXPlanetEngine에 의해 오직 한번 호출 된다. (Overrides NXRenderLayerInitialize)
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:251`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:59`

## Lock
- Description: 벡터 객체 편집 과정을 쓰레드 간에 접근하지 못하도록 제한한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:214`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:137`

## Modify
- Description: 원본 객체와 수정 객체를 입력하여 편집 스택에 추가한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:57`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:260`

## SelectNone
- Description: 객체 선택을 해제한다. 객체가 선택되면 이를 해제한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:152`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:205`

## SelectObject
- Description: 여러 개의 객체 중 하나의 객체만을 선택한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:157`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:211`

## SetEditBase
- Description: 이 레이어 밖에서 생성된 XvcBase 인스턴스를 설정한다. 외부 XvcBase를 설정하면 새로이 생성되는 객체는 외부 XvcBase에 추가된다.
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:195`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:93`

## SetLayerDisplayOrder
- Description: 편집 베이스(EditBase)의 레이어(XvcLayer)의 ID를 배열에 차례로 저장하여 도시 순서를 설정한다. UsableLayerDisplayOrder가 true로 설정되어 있어야 하며, 맨 처음 항목의 XvcLayer가 먼저 도시된다.
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:210`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:120`

## UnLock
- Description: 벡터 객체 편집 제한을 해제한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerVectorEditor.h:218`
- Implementation: `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:143`
