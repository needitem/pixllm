---
title: Pixoneer.NXDL.NXMilmap.NXMilmapToolBox Methods
aliases:
  - NXMilmapToolBox Methods
  - Pixoneer.NXDL.NXMilmap.NXMilmapToolBox
  - NXMilmapToolBox
symbols:
  - NXMilmapToolBox
  - GetResultGeoPoints
  - GetResultStrings
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nxmilmap
---

# Overview
- Namespace: `Pixoneer.NXDL.NXMilmap`
- Type: `NXMilmapToolBox`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXMilmap_NXMilmapToolBox.htm`
- Type declaration: `Source/NXMilmap/NXMilmapView.h:25`
- Method count: `2`

## GetResultGeoPoints
- Description: 측정에 사용된 위경도 정점 배열을 반환한다. DistanceMeasurer : 시작점과 끝점 PathMeasurer : 폴리라인을 이루는 정점 AreaMeasurer : 영역을 이루는 정점 CircleMeasurer : 원형 측정 중심(첫번째 정점), 원형 측정 중심과 반지름을 결정하는 정점(두번째 정점) AngleMeasurer : 각도 측정 줌심(첫번째 정점), 중심을 기준으로 azimuth를 결정하는 정점(두번째 정점)
- Declaration: `not found`
- Implementation: `Source/NXMilmap/NXMilmapToolBox.cpp:138`

## GetResultStrings
- Description: 측정 결과 문자열을 반환한다. DistanceMeasurer, AreaMeasurer, AngleMeasurer : 각 측정모드에 따른 결과 1개 CircleMeasurer : 면적(첫번째 문자열), 두 정점의 거리(반지름, 두번째 문자열) PathMeasurer : 폴리라인을 이루는 각 선분으로 계산되는 거리
- Declaration: `not found`
- Implementation: `Source/NXMilmap/NXMilmapToolBox.cpp:160`
