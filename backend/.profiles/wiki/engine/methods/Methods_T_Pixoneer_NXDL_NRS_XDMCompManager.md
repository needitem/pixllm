---
title: Pixoneer.NXDL.NRS.XDMCompManager Methods
aliases:
  - XDMCompManager Methods
  - Pixoneer.NXDL.NRS.XDMCompManager
  - XDMCompManager
symbols:
  - XDMCompManager
  - AddXDMComposite
  - AddXDMCompositeTail
  - CalcBandRange
  - CalcCompRange
  - CalcTotalRange
  - GetNativePtr
  - GetXDMCompositeAt
  - HitTest
  - MoveComposite
  - RefreshWarpCoeff
  - RemoveXDMComposite
  - RemoveXDMCompositeAll
  - RemoveXDMCompositeAt
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
- Type: `XDMCompManager`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XDMCompManager.htm`
- Type declaration: `Source/NXDLrs/NXDLrs.h:1840`
- Method count: `13`

## AddXDMComposite
- Description: 색합성 인스턴스를 배열의 제일 앞에 추가한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1867`
- Implementation: `Source/NXDLrs/XDMCompManager.cpp:68`

## AddXDMCompositeTail
- Description: 색합성 인스턴스를 배열의 제일 마지막에 추가한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1872`
- Implementation: `Source/NXDLrs/XDMCompManager.cpp:83`

## CalcBandRange
- Description: 특정 밴드의 경계 영역을 계산한다. XDMCompManager의 좌표계를 기준으로 하여 계산한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1921`
- Implementation: `Source/NXDLrs/XDMCompManager.cpp:217`

## CalcCompRange
- Description: 특정 색합성 인스턴스의 경계영역을 계산한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1912`
- Implementation: `Source/NXDLrs/XDMCompManager.cpp:203`

## CalcTotalRange
- Description: XDMCompManager에서 관리되는 모든 색합성 인스턴스의 경계 영역을 계산한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1903`
- Implementation: `Source/NXDLrs/XDMCompManager.cpp:191`

## GetNativePtr
- Description: XDMCompManager 원본 비관리 객체 포인터를 가져온다. c# 사용 불가.
- Declaration: `Source/NXDLrs/NXDLrs.h:1862`
- Implementation: `not found`

## GetXDMCompositeAt
- Description: 입력 인덱스에 대한 색합성 인스턴스를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1877`
- Implementation: `Source/NXDLrs/XDMCompManager.cpp:98`

## HitTest
- Description: 화면에 도시된 XDMComposite 중에서 특정 위치에 Hitting 되는 가장 상위의 XDMComposite 를 가져온다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1931`
- Implementation: `Source/NXDLrs/XDMCompManager.cpp:239`

## MoveComposite
- Description: 색합성 순서를 변경한다. Composite는 배열의 순서대로 영상을 도시하기 때문에 이 함수를 통해 영상도시 순서를 변경할 수 있다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1895`
- Implementation: `Source/NXDLrs/XDMCompManager.cpp:171`

## RefreshWarpCoeff
- Description: XDMComposite의 WarpCoeff(변환식 계수)를 재계산한다. 영상을 임의로 이동 및 회전하여 Composite 영역이 변경되었을 경우 변경된 영역에 해당하는 WarpCoeff를 다시 계산한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1925`
- Implementation: `Source/NXDLrs/XDMCompManager.cpp:231`

## RemoveXDMComposite
- Description: 입력 XDMComposite객체와 동일한 객체를 내부 관리 배열에서 삭제한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1884`
- Implementation: `Source/NXDLrs/XDMCompManager.cpp:117`

## RemoveXDMCompositeAll
- Description: Manager에서 관리되는 XDMComposite를 모두 삭제한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1880`
- Implementation: `Source/NXDLrs/XDMCompManager.cpp:107`

## RemoveXDMCompositeAt
- Description: 입력 인덱스에 있는 XDMComposite를 삭제한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1888`
- Implementation: `Source/NXDLrs/XDMCompManager.cpp:127`
