---
title: Pixoneer.NXDL.NRS.XDMBandGeoCorrect Methods
aliases:
  - XDMBandGeoCorrect Methods
  - Pixoneer.NXDL.NRS.XDMBandGeoCorrect
  - XDMBandGeoCorrect
symbols:
  - XDMBandGeoCorrect
  - CalcSourcePixelBound
  - GetInputParam
  - SetInputParam
  - WarpPointImage2Map
  - WarpPointMap2Image
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
- Type: `XDMBandGeoCorrect`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XDMBandGeoCorrect.htm`
- Type declaration: `Source/NXDLrs/XDMBandGeoCorrect.h:162`
- Method count: `5`

## CalcSourcePixelBound
- Description: 파라미터로 입력된 XGCPSets객체로부터 Map to Image변환 관계를 이용하여 지리좌표로 부터 이미지 좌표계로 변환시킨다.
- Declaration: `Source/NXDLrs/XDMBandGeoCorrect.h:195`
- Implementation: `Source/NXDLrs/XDMBandGeoCorrect.cpp:128`

## GetInputParam
- Description: 기하보정 수행을 위한 입력 파라미터를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandGeoCorrect.h:183`
- Implementation: `Source/NXDLrs/XDMBandGeoCorrect.cpp:123`

## SetInputParam
- Description: 기하보정을 위한 입력 파라미터를 설정한다.
- Declaration: `Source/NXDLrs/XDMBandGeoCorrect.h:178`
- Implementation: `Source/NXDLrs/XDMBandGeoCorrect.cpp:78`

## WarpPointImage2Map
- Description: 파라미터로 입력된 XGCPSets객체로부터 Image to Map변환 관계를 이용하여 이미지좌표를 지리 좌표로 변환시킨다.
- Declaration: `Source/NXDLrs/XDMBandGeoCorrect.h:213`
- Implementation: `Source/NXDLrs/XDMBandGeoCorrect.cpp:150`

## WarpPointMap2Image
- Description: 파라미터로 입력된 XGCPSets객체로부터 Map to Image변환 관계를 이용하여 지리좌표를 이미지 좌표로 변환시킨다.
- Declaration: `Source/NXDLrs/XDMBandGeoCorrect.h:204`
- Implementation: `Source/NXDLrs/XDMBandGeoCorrect.cpp:139`
