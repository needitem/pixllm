---
title: Pixoneer.NXDL.NXImage.NXImageLayerCompLink Methods
aliases:
  - NXImageLayerCompLink Methods
  - Pixoneer.NXDL.NXImage.NXImageLayerCompLink
  - NXImageLayerCompLink
symbols:
  - NXImageLayerCompLink
  - EnableCache
  - GetXDLCompManager1
  - GetXDLCompManager2
  - Invalidate
  - Lock
  - SetComp1Front
  - SetComp2Front
  - UnLock
  - ZoomFit
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nximage
---

# Overview
- Namespace: `Pixoneer.NXDL.NXImage`
- Type: `NXImageLayerCompLink`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXImage_NXImageLayerCompLink.htm`
- Type declaration: `Source/NXImage/NXImageLayerCompLink.h:151`
- Method count: `9`

## EnableCache
- Description: 캐싱을 활성화한다.
- Declaration: `Source/NXImage/NXImageLayerCompLink.h:217`
- Implementation: `Source/NXImage/NXImageLayerCompLink.cpp:150`

## GetXDLCompManager1
- Description: 첫번째 Composite 레이어의 Composite manager를 가져온다.
- Declaration: `Source/NXImage/NXImageLayerCompLink.h:184`
- Implementation: `Source/NXImage/NXImageLayerCompLink.cpp:57`

## GetXDLCompManager2
- Description: 두번째 Composite 레이어의 Composite manager를 가져온다.
- Declaration: `Source/NXImage/NXImageLayerCompLink.h:188`
- Implementation: `Source/NXImage/NXImageLayerCompLink.cpp:62`

## Invalidate
- Description: 전체 화면을 갱신하도록 하며, 컨트롤의 내용을 다시 그리도록 한다.
- Declaration: `Source/NXImage/NXImageLayerCompLink.h:196`
- Implementation: `Source/NXImage/NXImageLayerCompLink.cpp:52`

## Lock
- Description: 두 개의 Composite 레이어의 XDMCompManager 객체를 다른 쓰레드에서 변경하지 못하도록 제한한다.
- Declaration: `Source/NXImage/NXImageLayerCompLink.h:208`
- Implementation: `Source/NXImage/NXImageLayerCompLink.cpp:140`

## SetComp1Front
- Description: 첫번째 Composite 레이어를 앞쪽으로 이동한다.
- Declaration: `Source/NXImage/NXImageLayerCompLink.h:200`
- Implementation: `Source/NXImage/NXImageLayerCompLink.cpp:67`

## SetComp2Front
- Description: 두번째 Composite 레이어를 앞쪽으로 이동한다.
- Declaration: `Source/NXImage/NXImageLayerCompLink.h:204`
- Implementation: `Source/NXImage/NXImageLayerCompLink.cpp:78`

## UnLock
- Description: 두 개의 Composite 레이어의 XDMCompManager 객체의 제한 설정을 해제한다.
- Declaration: `Source/NXImage/NXImageLayerCompLink.h:212`
- Implementation: `Source/NXImage/NXImageLayerCompLink.cpp:145`

## ZoomFit
- Description: 화면에 전체 영상이 도시되도록 확대축소하는 함수이다.
- Declaration: `Source/NXImage/NXImageLayerCompLink.h:192`
- Implementation: `Source/NXImage/NXImageLayerCompLink.cpp:47`
