---
title: Pixoneer.NXDL.NSM.XSensorModel Methods
aliases:
  - XSensorModel Methods
  - Pixoneer.NXDL.NSM.XSensorModel
  - XSensorModel
symbols:
  - XSensorModel
  - GetMapCoordOfImageCenter
  - GetNativePtr
  - ImageToWorldE
  - ImageToWorldG
  - WorldToImageE
  - WorldToImageG
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
- Type: `XSensorModel`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSM_XSensorModel.htm`
- Type declaration: `Source/NXDLsm/NXDLsm.h:42`
- Method count: `6`

## GetMapCoordOfImageCenter
- Description: 이미지의 센터 지리 좌표값(ECEF).
- Declaration: `Source/NXDLsm/NXDLsm.h:81`
- Implementation: `Source/NXDLsm/XSensorModel.cpp:83`

## GetNativePtr
- Description: XSensorModel 원본 비관리 객체 포인터를 가져온다. c# 사용 불가.
- Declaration: `Source/NXDLsm/NXDLsm.h:85`
- Implementation: `not found`

## ImageToWorldE
- Description: 이미지좌표로부터 ECEF좌표점으로 변환한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:64`
- Implementation: `Source/NXDLsm/XSensorModel.cpp:52`

## ImageToWorldG
- Description: 이미지 좌표값으로부터 위경도 좌표값으로 변경한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:77`
- Implementation: `Source/NXDLsm/XSensorModel.cpp:72`

## WorldToImageE
- Description: ECEF 좌표점으로부터 이미지좌표로 변환한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:57`
- Implementation: `Source/NXDLsm/XSensorModel.cpp:42`

## WorldToImageG
- Description: 위경도 좌표값으로부터 이미지 좌표로 변경한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:70`
- Implementation: `Source/NXDLsm/XSensorModel.cpp:62`
