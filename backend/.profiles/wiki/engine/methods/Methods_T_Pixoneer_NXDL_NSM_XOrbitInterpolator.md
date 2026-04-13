---
title: Pixoneer.NXDL.NSM.XOrbitInterpolator Methods
aliases:
  - XOrbitInterpolator Methods
  - Pixoneer.NXDL.NSM.XOrbitInterpolator
  - XOrbitInterpolator
symbols:
  - XOrbitInterpolator
  - AddStateVector
  - ClearStateVector
  - GetStateVector
  - HermiteInterpolate
  - IsValid
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nsm
---

# Overview
- Namespace: `Pixoneer.NXDL.NSM`
- Type: `XOrbitInterpolator`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSM_XOrbitInterpolator.htm`
- Type declaration: `Source/NXDLsm/NXDLsm.h:674`
- Method count: `5`

## AddStateVector
- Description: 상태 벡터를 추가한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:690`
- Implementation: `Source/NXDLsm/XOrbitInterpolator.cpp:41`

## ClearStateVector
- Description: 저장된 모든 상태 벡터를 삭제한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:714`
- Implementation: `Source/NXDLsm/XOrbitInterpolator.cpp:97`

## GetStateVector
- Description: 특정 순서의 상태 벡터를 가져온다.
- Declaration: `Source/NXDLsm/NXDLsm.h:698`, `Source/NXDLsm/NXDLsm.h:707`
- Implementation: `Source/NXDLsm/XOrbitInterpolator.cpp:47`, `Source/NXDLsm/XOrbitInterpolator.cpp:68`

## HermiteInterpolate
- Description: 특정 시간에 대한 에르미트 보간법(Hermite interpolation)을 실행하고 그 때의 상태 벡터 값을 가져온다.
- Declaration: `Source/NXDLsm/NXDLsm.h:722`
- Implementation: `Source/NXDLsm/XOrbitInterpolator.cpp:103`

## IsValid
- Description: 특정 시간에 대해서 상태벡터의 보간이 가능한지 확인한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:711`
- Implementation: `Source/NXDLsm/XOrbitInterpolator.cpp:91`
