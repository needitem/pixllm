---
title: Pixoneer.NXDL.NDFS.XPBIProviderExporter Methods
aliases:
  - XPBIProviderExporter Methods
  - Pixoneer.NXDL.NDFS.XPBIProviderExporter
  - XPBIProviderExporter
symbols:
  - XPBIProviderExporter
  - Cancel
  - Export2PBI
  - GetPercent
  - SetSource
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
- Type: `XPBIProviderExporter`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NDFS_XPBIProviderExporter.htm`
- Type declaration: `Source/NXDLdfs/NXDLdfs.h:164`
- Method count: `4`

## Cancel
- Description: 현재 저장중인 프로세스를 취소한다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:208`
- Implementation: `Source/NXDLdfs/XPBIProviderExporter.cpp:88`

## Export2PBI
- Description: XDMCompManager객체로부터 소스를 입력받아 PBI파일로 저장한다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:202`
- Implementation: `Source/NXDLdfs/XPBIProviderExporter.cpp:68`

## GetPercent
- Description: 저장 프로세스 공정 중 진행율을 퍼센트로 얻는다
- Declaration: `Source/NXDLdfs/NXDLdfs.h:216`
- Implementation: `Source/NXDLdfs/XPBIProviderExporter.cpp:93`

## SetSource
- Description: XDMCompManager 객체를 입력받아 내부에 관리되는 Composite들의 최대 Boundary값을 계산하고 해당 영역에 대한 만들어 낼수 있는 최소/최대 Level을 계산한다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:187`
- Implementation: `Source/NXDLdfs/XPBIProviderExporter.cpp:37`
