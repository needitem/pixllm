---
title: Pixoneer.NXDL.NXPlanet.NXPlanetEngine Methods
aliases:
  - NXPlanetEngine Methods
  - Pixoneer.NXDL.NXPlanet.NXPlanetEngine
  - NXPlanetEngine
symbols:
  - NXPlanetEngine
  - AddPBIGroup
  - AttachViewArea
  - DetachViewArea
  - GetViewArea
  - GetViewAreaUnderMouse
  - OnSize
  - PreTranslateMessage
  - RegisterPBIProvider
  - Release
  - RemovePBIGroup
  - ResetSupportPlanetMode
  - SetPBPDefaultDataSet
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
- Type: `NXPlanetEngine`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXPlanet_NXPlanetEngine.htm`
- Type declaration: `Source/NXPlanet/NXPlanetEngine.h:27`
- Method count: `12`

## AddPBIGroup
- Description: PBI 데이터 소스를 엔진에 추가한다.
- Declaration: `Source/NXPlanet/NXPlanetEngine.h:87`
- Implementation: `Source/NXPlanet/NXPlanetEngine.cpp:304`

## AttachViewArea
- Description: 뷰 영역에 엔진을 연결하고, 윈도우에 뷰가 생성 될 때 자동으로 불린다.
- Declaration: `Source/NXPlanet/NXPlanetEngine.h:37`
- Implementation: `Source/NXPlanet/NXPlanetEngine.cpp:88`

## DetachViewArea
- Description: 엔진으로부터 뷰 구역을 분리하고, 윈도우에 의해 뷰가 파괴 될 때 자동으로 불린다.
- Declaration: `Source/NXPlanet/NXPlanetEngine.h:58`, `Source/NXPlanet/NXPlanetEngine.h:66`
- Implementation: `Source/NXPlanet/NXPlanetEngine.cpp:193`, `Source/NXPlanet/NXPlanetEngine.cpp:198`

## GetViewArea
- Description: ID에 의해 뷰를 가져온다
- Declaration: `Source/NXPlanet/NXPlanetEngine.h:42`, `Source/NXPlanet/NXPlanetEngine.h:49`
- Implementation: `Source/NXPlanet/NXPlanetEngine.cpp:161`, `Source/NXPlanet/NXPlanetEngine.cpp:172`

## GetViewAreaUnderMouse
- Description: 마우스 아래에 있는 뷰를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetEngine.h:53`
- Implementation: `Source/NXPlanet/NXPlanetEngine.cpp:181`

## OnSize
- Description: 윈도우 메세지 창의 크기를 조정하며, 엔진 메세지 필터가 크기 조절 될 때 자동으로 불린다.
- Declaration: `Source/NXPlanet/NXPlanetEngine.h:73`
- Implementation: `Source/NXPlanet/NXPlanetEngine.cpp:287`

## PreTranslateMessage
- Description: 윈도우 창에서 사전에 메세지가 바뀌게 될 때, 엔진 메세지 필터에 의해 자동으로 불린다.
- Declaration: `Source/NXPlanet/NXPlanetEngine.h:78`
- Implementation: `Source/NXPlanet/NXPlanetEngine.cpp:212`

## RegisterPBIProvider
- Description: 새로운 PBI 형식을 지원하는 데이터 제공자를 등록한다.
- Declaration: `Source/NXPlanet/NXPlanetEngine.h:103`
- Implementation: `Source/NXPlanet/NXPlanetEngine.cpp:382`

## Release
- Description: 엔진을 제거한다.
- Declaration: `Source/NXPlanet/NXPlanetEngine.h:61`
- Implementation: `Source/NXPlanet/NXPlanetEngine.cpp:60`

## RemovePBIGroup
- Description: 엔진에서 PBI 데이터 소스를 제거한다.
- Declaration: `Source/NXPlanet/NXPlanetEngine.h:92`
- Implementation: `Source/NXPlanet/NXPlanetEngine.cpp:298`

## ResetSupportPlanetMode
- Description: Planet 모드를 초기화한다.
- Declaration: `Source/NXPlanet/NXPlanetEngine.h:82`
- Implementation: `Source/NXPlanet/NXPlanetEngine.cpp:362`

## SetPBPDefaultDataSet
- Description: PBI 데이터 소스가 설정되며 바뀐 데이터로 Planet 레어어를 랜더링한다
- Declaration: `Source/NXPlanet/NXPlanetEngine.h:97`
- Implementation: `Source/NXPlanet/NXPlanetEngine.cpp:340`
