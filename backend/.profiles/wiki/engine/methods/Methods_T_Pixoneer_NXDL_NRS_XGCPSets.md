---
title: Pixoneer.NXDL.NRS.XGCPSets Methods
aliases:
  - XGCPSets Methods
  - Pixoneer.NXDL.NRS.XGCPSets
  - XGCPSets
symbols:
  - XGCPSets
  - AddGCP
  - GetGCP
  - GetNumGCP
  - GetWarpCoeffImg2Map
  - GetWarpCoeffMap2Img
  - LoadGCPSet
  - Remove
  - RemoveAllGCP
  - SaveGCPSet
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
- Type: `XGCPSets`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XGCPSets.htm`
- Type declaration: `Source/NXDLrs/NXDLrs.h:127`
- Method count: `9`

## AddGCP
- Description: GCP 인스턴스를 GCP Set에 추가한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:140`
- Implementation: `Source/NXDLrs/XGCPSet.cpp:110`

## GetGCP
- Description: 입력 인덱스에 해당하는 XGCP 인스턴스를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:145`
- Implementation: `Source/NXDLrs/XGCPSet.cpp:118`

## GetNumGCP
- Description: GCP Set에 있는 GCP 개수를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:151`
- Implementation: `Source/NXDLrs/XGCPSet.cpp:125`

## GetWarpCoeffImg2Map
- Description: GCP Set에 있는 GCP를 이용하여 영상 좌표에서 지리 좌표로 변환할 때 필요한 Warping 계수를 반환한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:167`, `Source/NXDLrs/NXDLrs.h:180`
- Implementation: `Source/NXDLrs/XGCPSet.cpp:145`, `Source/NXDLrs/XGCPSet.cpp:157`

## GetWarpCoeffMap2Img
- Description: GCP Set에 있는 GCP를 이용하여 지리 좌표에서 영상 좌표로 변환할 때 필요한 Warping 계수(XWarpCoeff객체의 정의)들을 얻을 수 있다.
- Declaration: `Source/NXDLrs/NXDLrs.h:187`, `Source/NXDLrs/NXDLrs.h:199`
- Implementation: `Source/NXDLrs/XGCPSet.cpp:250`, `Source/NXDLrs/XGCPSet.cpp:258`

## LoadGCPSet
- Description: XML 형식의 파일로부터 GCP를 읽어 추가한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:206`
- Implementation: `Source/NXDLrs/XGCPSet.cpp:350`

## Remove
- Description: GCP Set에 있는 특정 GCP를 삭제한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:162`
- Implementation: `Source/NXDLrs/XGCPSet.cpp:137`

## RemoveAllGCP
- Description: GCP Set에 있는 모든 GCP를 삭제한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:156`
- Implementation: `Source/NXDLrs/XGCPSet.cpp:131`

## SaveGCPSet
- Description: GCP Set의 데이터 및 정보를 파일로 저장한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:213`
- Implementation: `Source/NXDLrs/XGCPSet.cpp:512`
