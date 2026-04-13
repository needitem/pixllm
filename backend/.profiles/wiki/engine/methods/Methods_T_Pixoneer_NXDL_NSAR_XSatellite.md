---
title: Pixoneer.NXDL.NSAR.XSatellite Methods
aliases:
  - XSatellite Methods
  - Pixoneer.NXDL.NSAR.XSatellite
  - XSatellite
symbols:
  - XSatellite
  - ClearEOPData
  - Dispose
  - EciFromEcr
  - EciToEcr
  - EcrToEci
  - GetGST
  - Gregorian2ModifiedJulian
  - LoadEOPData
  - ModifiedJulian2Gregorian
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nsar
---

# Overview
- Namespace: `Pixoneer.NXDL.NSAR`
- Type: `XSatellite`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSAR_XSatellite.htm`
- Type declaration: `Source/NXDLsar/NXDLsar.h:369`
- Method count: `9`

## ClearEOPData
- Description: Earth Orientation Parameter(EOP) Data를 제거하여 초기화를 수행한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:397`
- Implementation: `Source/NXDLsar/XSatellite.cpp:80`

## Dispose
- Description: No description in HTML reference.
- Declaration: `not found`
- Implementation: `not found`

## EciFromEcr
- Description: Modified Julian Date에 대응하는 ECR 좌표계 값을 ECI 좌표계 값으로 변환하는 행렬을 제공한다. 변환행렬은 3x3 크기의 행렬을 가지며 위치에 대한 변환 행렬을 의미한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:435`
- Implementation: `Source/NXDLsar/XSatellite.cpp:161`

## EciToEcr
- Description: Modified Julian Date에 대응하는 ECI좌표계의 값(위치, 속도)을 ECR 좌표계값으로 변환한다. 입력된 위치 값이 null 값을 가지면 변환이 실패하며, 입력된 속도 값이 null 값일 때는 위치만 변환되어 출력된다.
- Declaration: `Source/NXDLsar/NXDLsar.h:426`
- Implementation: `Source/NXDLsar/XSatellite.cpp:128`

## EcrToEci
- Description: Modified Julian Date에 대응하는 ECR좌표계의 값(위치, 속도)을 ECI 좌표계값으로 변환한다. 입력된 위치 값이 null 값을 가지면 변환이 실패하며, 입력된 속도 값이 null 값일 때는 위치만 변환되어 출력된다.
- Declaration: `Source/NXDLsar/NXDLsar.h:415`
- Implementation: `Source/NXDLsar/XSatellite.cpp:94`

## GetGST
- Description: Modified Julian Date에 대응하는 Greenwich sidereal time을 계산한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:404`
- Implementation: `Source/NXDLsar/XSatellite.cpp:85`

## Gregorian2ModifiedJulian
- Description: UTC 기준의 날짜(Gregorian, 년월일시분초)를 수정된 율리우스 일(Modified Julian Day)로 변경한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:447`
- Implementation: `Source/NXDLsar/XSatellite.cpp:69`

## LoadEOPData
- Description: 정밀한 ECI 좌표계 변환을 위하여 Earth Orientation Parameter(EOP) Data를 지정한다. EOP 파일 지정이 없을 때는 Greenwich sidereal time 값만 적용하여 ECI 좌표계 계산이 수행된다. http://celestrak.com/SpaceData/ 사이트에서 CSV 형태의 데이터를 구할 수 있다. 파일은 "*.csv" 형태로 csv 확장자를 가져야 한다. CSV 데이터 구조 : DATE,MJD,X,Y,UT1-UTC,LOD,DPSI,DEPS,DX,DY,DAT,DATA_TYPE
- Declaration: `Source/NXDLsar/NXDLsar.h:392`
- Implementation: `Source/NXDLsar/XSatellite.cpp:74`

## ModifiedJulian2Gregorian
- Description: 수정된 율리우스 일(Modified Julian Day)을 UTC 기준의 날짜(Gregorian, 년월일시분초)로 변경한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:459`
- Implementation: `Source/NXDLsar/XSatellite.cpp:54`
