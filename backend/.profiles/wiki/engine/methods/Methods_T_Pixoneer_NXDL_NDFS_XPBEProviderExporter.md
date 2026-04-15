---
title: Pixoneer.NXDL.NDFS.XPBEProviderExporter Methods
aliases:
  - XPBEProviderExporter Methods
  - Pixoneer.NXDL.NDFS.XPBEProviderExporter
  - XPBEProviderExporter
symbols:
  - XPBEProviderExporter
  - Cancel
  - Export2PBE
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
- Type: `XPBEProviderExporter`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NDFS_XPBEProviderExporter.htm`
- Type declaration: `Source/NXDLdfs/NXDLdfs.h:256`
- Method count: `4`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NDFS.XPBEProviderExporter
type_name: XPBEProviderExporter
namespace: Pixoneer.NXDL.NDFS
method_section_prefix: "## "
verification_rules:
  - treat_declaration_lines_as_symbol_existence_evidence
  - treat_implementation_lines_as_source_anchor_evidence
  - prefer_this_page_over_examples_for_exact_call_shapes
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page to verify exact symbol existence before emitting code.
- Cross-check declaration and implementation lines when overloads or call shapes matter.
- Treat examples and workflow pages as composition guidance, but treat this page as the canonical member list.
## Cancel
- Description: 현재 저장 중인 프로세스를 취소한다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:311`
- Implementation: `Source/NXDLdfs/XPBEProviderExporter.cpp:132`

## Export2PBE
- Description: SetSource 함수를 통해 설정된 입력 데이터를 이용하여 PBE(Pixoneer Base Elevation) 파일을 생성한다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:306`
- Implementation: `Source/NXDLdfs/XPBEProviderExporter.cpp:117`

## GetPercent
- Description: 저장 프로세스 공정 중 진행율을 백분율로 얻는다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:317`
- Implementation: `Source/NXDLdfs/XPBEProviderExporter.cpp:137`

## SetSource
- Description: PBE 생성을 위한 입력으로 XDMBand 객체를 설정한다
- Declaration: `Source/NXDLdfs/NXDLdfs.h:279`, `Source/NXDLdfs/NXDLdfs.h:292`
- Implementation: `Source/NXDLdfs/XPBEProviderExporter.cpp:38`, `Source/NXDLdfs/XPBEProviderExporter.cpp:87`
