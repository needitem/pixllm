---
title: Pixoneer.NXDL.NCC.Xcc Methods
aliases:
  - Xcc Methods
  - Pixoneer.NXDL.NCC.Xcc
  - Xcc
symbols:
  - Xcc
  - CalcGeodeticAngle
  - CalcGeodeticArea
  - CalcGeodeticDistance
  - CalcGeodeticIntersect
  - ConvPixelSize
  - GEOREF2WGP
  - MGRS2UTM
  - MGRS2WGP
  - UTM2MGRS
  - UTM2WGP
  - WGP2GEOREF
  - WGP2MGRS
  - WGP2UTM
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - ncc
---

# Overview
- Namespace: `Pixoneer.NXDL.NCC`
- Type: `Xcc`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NCC_Xcc.htm`
- Type declaration: `Source/NXDLcc/NXDLcc.h:316`
- Method count: `13`

## CalcGeodeticAngle
- Description: 지구 타원체 상에서 특정 지점을 원점(Center)으로 하고 임의의 두 점 사이 각도를 계산한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:563`
- Implementation: `Source/NXDLcc/NXDLcc.cpp:27`

## CalcGeodeticArea
- Description: 입력 위경도 좌표배열로 이루어진 영역의 타원체 상의 면적을 계산한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:640`
- Implementation: `Source/NXDLcc/NXDLcc.cpp:55`, `Source/NXDLcc/NXDLcc.cpp:73`

## CalcGeodeticDistance
- Description: Geographic 좌표계상에서 두개의 지점으로부터 타원체상으로의 거리를 측정한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:551`
- Implementation: `Source/NXDLcc/NXDLcc.cpp:21`

## CalcGeodeticIntersect
- Description: 두 개의 geodesics의 교점을 계산한다. (높이값은 무시된다.)
- Declaration: `Source/NXDLcc/NXDLcc.h:648`
- Implementation: `Source/NXDLcc/NXDLcc.cpp:80`, `Source/NXDLcc/NXDLcc.cpp:91`

## ConvPixelSize
- Description: In 지리좌표계에서 Out좌표계로의 해상도(공간적 화소 크기)를 변환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:635`
- Implementation: `Source/NXDLcc/NXDLcc.cpp:42`, `Source/NXDLcc/NXDLcc.cpp:49`

## GEOREF2WGP
- Description: GEOREF 좌표계로부터 WGP 좌표계로 변환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:605`
- Implementation: `Source/NXDLcc/XCoordinateTransform.cpp:220`

## MGRS2UTM
- Description: MGRS 좌표계로부터 UTM 좌표계로 변환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:522`
- Implementation: `Source/NXDLcc/XCoordinateTransform.cpp:180`

## MGRS2WGP
- Description: MGRS 좌표계로부터 Geographic좌표계로 변환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:541`
- Implementation: `Source/NXDLcc/XCoordinateTransform.cpp:195`

## UTM2MGRS
- Description: UTM 좌표계로부터 MGRS 좌표계로 변환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:483`, `Source/NXDLcc/NXDLcc.h:503`
- Implementation: `Source/NXDLcc/XCoordinateTransform.cpp:166`, `Source/NXDLcc/XCoordinateTransform.cpp:171`

## UTM2WGP
- Description: UTM 좌표계로부터 Geographic 좌표계로 변환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:464`
- Implementation: `Source/NXDLcc/XCoordinateTransform.cpp:154`

## WGP2GEOREF
- Description: Geographic 좌표를 GEOREF(World Geographic Reference)좌표계로 변환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:587`
- Implementation: `Source/NXDLcc/XCoordinateTransform.cpp:209`

## WGP2MGRS
- Description: Geographic좌표계를 MGRS좌표계로 변환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:419`, `Source/NXDLcc/NXDLcc.h:442`
- Implementation: `Source/NXDLcc/XCoordinateTransform.cpp:139`, `Source/NXDLcc/XCoordinateTransform.cpp:144`

## WGP2UTM
- Description: Geographic 좌표 시스템으로부터 UTM 좌표 시스템으로 변환을 수행한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:344`, `Source/NXDLcc/NXDLcc.h:370`, `Source/NXDLcc/NXDLcc.h:397`
- Implementation: `Source/NXDLcc/XCoordinateTransform.cpp:82`, `Source/NXDLcc/XCoordinateTransform.cpp:97`, `Source/NXDLcc/XCoordinateTransform.cpp:115`
