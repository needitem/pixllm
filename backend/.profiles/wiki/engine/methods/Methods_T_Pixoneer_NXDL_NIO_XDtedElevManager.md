---
title: Pixoneer.NXDL.NIO.XDtedElevManager Methods
aliases:
  - XDtedElevManager Methods
  - Pixoneer.NXDL.NIO.XDtedElevManager
  - XDtedElevManager
symbols:
  - XDtedElevManager
  - GenerateXDMBandTileMerge
  - GetHeightAboveMSL
  - Open
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nio
---

# Overview
- Namespace: `Pixoneer.NXDL.NIO`
- Type: `XDtedElevManager`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NIO_XDtedElevManager.htm`
- Type declaration: `Source/NXDLio/NXDLio.h:949`
- Method count: `3`

## GenerateXDMBandTileMerge
- Description: DTED의 일부 영역에 대한 고도값을 얻기 위해 XDMBandTileMerge 객체를 생성한다.
- Declaration: `Source/NXDLio/NXDLio.h:976`
- Implementation: `Source/NXDLio/XDtedElevManager.cpp:54`

## GetHeightAboveMSL
- Description: 입력 좌표점에 대한 Mean SeaLevel상의 고도값을 얻는다. 입력 좌표 주변값을 이용하여 Bilinear interpolation을 한다.
- Declaration: `Source/NXDLio/NXDLio.h:968`
- Implementation: `Source/NXDLio/XDtedElevManager.cpp:49`

## Open
- Description: 로컬 디스크의 DTED가 존재하는 Folder를 입력하여 DTED값을 추출가능하도록 준비한다.
- Declaration: `Source/NXDLio/NXDLio.h:963`
- Implementation: `Source/NXDLio/XDtedElevManager.cpp:42`
