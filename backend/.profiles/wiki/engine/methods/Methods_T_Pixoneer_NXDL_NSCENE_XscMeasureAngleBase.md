---
title: Pixoneer.NXDL.NSCENE.XscMeasureAngleBase Methods
aliases:
  - XscMeasureAngleBase Methods
  - Pixoneer.NXDL.NSCENE.XscMeasureAngleBase
  - XscMeasureAngleBase
symbols:
  - XscMeasureAngleBase
  - GetCenter
  - GetEnd
  - GetResultAngle
  - SetCenter
  - SetEnd
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
- Type: `XscMeasureAngleBase`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSCENE_XscMeasureAngleBase.htm`
- Type declaration: `Source/NXDLscene/NXDLscene.h:2734`
- Method count: `5`

## GetCenter
- Description: 각도를 이루는 3개의 정점 중 중점을 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2770`, `Source/NXDLscene/NXDLscene.h:2780`
- Implementation: `Source/NXDLscene/XscMeasureAngle.cpp:99`, `Source/NXDLscene/XscMeasureAngle.cpp:135`

## GetEnd
- Description: 각도를 이루는 3개의 정점 중 끝점을 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2776`, `Source/NXDLscene/NXDLscene.h:2784`
- Implementation: `Source/NXDLscene/XscMeasureAngle.cpp:117`, `Source/NXDLscene/XscMeasureAngle.cpp:152`

## GetResultAngle
- Description: 각도 측정 결과 중 각도를 확인한다. 단위는 degree. 유효하지 않으면 MAX_REAL64를 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2820`
- Implementation: `Source/NXDLscene/XscMeasureAngle.cpp:169`, `Source/NXDLscene/XscMeasureAzimuth.cpp:44`

## SetCenter
- Description: 각도를 이루는 3개의 정점 중 중점을 설정한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2749`, `Source/NXDLscene/NXDLscene.h:2759`
- Implementation: `Source/NXDLscene/XscMeasureAngle.cpp:40`, `Source/NXDLscene/XscMeasureAngle.cpp:68`

## SetEnd
- Description: 각도를 이루는 3개의 정점 중 끝점을 설정한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2755`, `Source/NXDLscene/NXDLscene.h:2763`
- Implementation: `Source/NXDLscene/XscMeasureAngle.cpp:54`, `Source/NXDLscene/XscMeasureAngle.cpp:84`
