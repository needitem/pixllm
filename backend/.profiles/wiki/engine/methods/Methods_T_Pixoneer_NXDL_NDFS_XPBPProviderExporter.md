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

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NDFS.XPBPProviderExporter
type_name: XPBPProviderExporter
namespace: Pixoneer.NXDL.NDFS
method_section_prefix: "## "
verification_rules:
  - treat_declaration_lines_as_symbol_existence_evidence
  - treat_implementation_lines_as_source_anchor_evidence
  - use_this_page_only_after_a_workflow_or_type_hint_narrows_scope
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page only as a verification layer after a workflow or explicit type hint identifies the target type.
- Cross-check declaration and implementation lines when overloads, properties, or call shapes matter.
- Do not synthesize end-to-end usage answers from this page alone.
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
