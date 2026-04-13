---
title: Pixoneer.NXDL.NIO.XRPFToc Methods
aliases:
  - XRPFToc Methods
  - Pixoneer.NXDL.NIO.XRPFToc
  - XRPFToc
symbols:
  - XRPFToc
  - GetBoundaryRecord
  - GetFrameFileName
  - GetZone
  - LoadFile
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
- Type: `XRPFToc`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NIO_XRPFToc.htm`
- Type declaration: `Source/NXDLio/NXDLio.h:1422`
- Method count: `4`

## GetBoundaryRecord
- Description: 입력 인덱스에 해당하는 XRPCBoundaryRecord객체를 얻는다. toc파일 안에는 보통 1개 이상의 Boundary Rectangle Record 정보가 포함되어 있다. 이객체로 부터 Boundary Rectangle Record에 대한 정보를 얻을 수 있다.
- Declaration: `Source/NXDLio/NXDLio.h:1471`
- Implementation: `Source/NXDLio/XRPFToc.cpp:83`

## GetFrameFileName
- Description: 입력 인덱스에 해당하는 Frame파일 이름을 얻는다.
- Declaration: `Source/NXDLio/NXDLio.h:1445`, `Source/NXDLio/NXDLio.h:1455`, `Source/NXDLio/NXDLio.h:1462`
- Implementation: `Source/NXDLio/XRPFToc.cpp:52`, `Source/NXDLio/XRPFToc.cpp:59`, `Source/NXDLio/XRPFToc.cpp:66`

## GetZone
- Description: 입력된 인덱스에 대한 XRPCBoundaryRecord상의 Zone을 직접 얻는다.
- Declaration: `Source/NXDLio/NXDLio.h:1476`
- Implementation: `Source/NXDLio/XRPFToc.cpp:176`

## LoadFile
- Description: RPF TOC을 파일을 로딩한다.
- Declaration: `Source/NXDLio/NXDLio.h:1436`
- Implementation: `Source/NXDLio/XRPFToc.cpp:43`
