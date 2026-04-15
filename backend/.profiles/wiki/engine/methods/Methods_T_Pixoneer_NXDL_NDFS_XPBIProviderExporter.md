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

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NDFS.XPBIProviderExporter
type_name: XPBIProviderExporter
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
