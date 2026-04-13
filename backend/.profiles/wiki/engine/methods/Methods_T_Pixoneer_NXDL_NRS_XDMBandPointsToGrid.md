---
title: Pixoneer.NXDL.NRS.XDMBandPointsToGrid Methods
aliases:
  - XDMBandPointsToGrid Methods
  - Pixoneer.NXDL.NRS.XDMBandPointsToGrid
  - XDMBandPointsToGrid
symbols:
  - XDMBandPointsToGrid
  - GenerateOutput
  - GetInputParam
  - SearchBoundInfo
  - SetInputParam
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nrs
---

# Overview
- Namespace: `Pixoneer.NXDL.NRS`
- Type: `XDMBandPointsToGrid`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XDMBandPointsToGrid.htm`
- Type declaration: `Source/NXDLrs/XDMBandPointsToGrid.h:146`
- Method count: `4`

## GenerateOutput
- Description: 입력된 점좌표 데이터들을 이용하여 출력 그리드 데이터로 변환한다.
- Declaration: `Source/NXDLrs/XDMBandPointsToGrid.h:175`
- Implementation: `Source/NXDLrs/XDMBandPointsToGrid.cpp:101`

## GetInputParam
- Description: 점좌표 데이터에서 그리드 형식의 데이터로 변환하는 입력 파라미터를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandPointsToGrid.h:168`
- Implementation: `Source/NXDLrs/XDMBandPointsToGrid.cpp:96`

## SearchBoundInfo
- Description: 입력 파일 경로의 데이터를 읽어 데이터의 공간 좌표값 중 최댓값과 최솟값을 계산한다.
- Declaration: `Source/NXDLrs/XDMBandPointsToGrid.h:190`
- Implementation: `Source/NXDLrs/XDMBandPointsToGrid.cpp:113`, `Source/NXDLrs/XDMBandPointsToGrid.cpp:134`, `Source/NXDLrs/XDMBandPointsToGrid.cpp:142`

## SetInputParam
- Description: 점좌표 데이터에서 그리드 형식의 데이터로 변환하기 위한 입력 파라미터를 설정한다.
- Declaration: `Source/NXDLrs/XDMBandPointsToGrid.h:162`
- Implementation: `Source/NXDLrs/XDMBandPointsToGrid.cpp:58`
