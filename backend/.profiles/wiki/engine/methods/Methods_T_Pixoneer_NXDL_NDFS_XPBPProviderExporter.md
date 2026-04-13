---
title: Pixoneer.NXDL.NDFS.XPBPProviderExporter Methods
aliases:
  - XPBPProviderExporter Methods
  - Pixoneer.NXDL.NDFS.XPBPProviderExporter
  - XPBPProviderExporter
symbols:
  - XPBPProviderExporter
  - AddPName
  - BuildPointCloud
  - Cancel
  - Export2PBP
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - ndfs
---

# Overview
- Namespace: `Pixoneer.NXDL.NDFS`
- Type: `XPBPProviderExporter`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NDFS_XPBPProviderExporter.htm`
- Type declaration: `Source/NXDLdfs/NXDLdfs.h:478`
- Method count: `4`

## AddPName
- Description: 지점을 추가한다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:494`
- Implementation: `Source/NXDLdfs/XPBPProviderExporter.cpp:35`

## BuildPointCloud
- Description: AddName 함수에 의해 추가된 수많은 지점에 대하여 고속 추출을 하기 위해 구조화시키는 작업을 수행한다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:501`
- Implementation: `Source/NXDLdfs/XPBPProviderExporter.cpp:61`

## Cancel
- Description: 현재 진행중인 작업을 취소한다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:512`
- Implementation: `Source/NXDLdfs/XPBPProviderExporter.cpp:41`

## Export2PBP
- Description: 저장된 지점들을 구조화하여 PBP에 저장한다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:507`
- Implementation: `Source/NXDLdfs/XPBPProviderExporter.cpp:46`
