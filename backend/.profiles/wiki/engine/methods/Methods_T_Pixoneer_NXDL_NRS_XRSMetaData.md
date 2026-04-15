---
title: Pixoneer.NXDL.NRS.XRSMetaData Methods
aliases:
  - XRSMetaData Methods
  - Pixoneer.NXDL.NRS.XRSMetaData
  - XRSMetaData
symbols:
  - XRSMetaData
  - GetDomainList
  - GetKeyList
  - GetValue
  - LoadXml
  - RemoveKey
  - SaveXml
  - SetValue
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
- Type: `XRSMetaData`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XRSMetaData.htm`
- Type declaration: `Source/NXDLrs/XRSFile.h:158`
- Method count: `7`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XRSMetaData
type_name: XRSMetaData
namespace: Pixoneer.NXDL.NRS
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
## GetDomainList
- Description: XRSLoadFile객체에 포함된 메타데이터로부터 카테고리 분류인 Domain List를 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:175`
- Implementation: `Source/NXDLrs/XRSMetaData.cpp:70`

## GetKeyList
- Description: XRSLoadFile객체에 포함된 메타데이터로부터 Key List를 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:178`, `Source/NXDLrs/XRSFile.h:183`
- Implementation: `Source/NXDLrs/XRSMetaData.cpp:88`, `Source/NXDLrs/XRSMetaData.cpp:93`

## GetValue
- Description: 특정 Key에 해당하는 Value값을 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:188`, `Source/NXDLrs/XRSFile.h:194`
- Implementation: `Source/NXDLrs/XRSMetaData.cpp:115`, `Source/NXDLrs/XRSMetaData.cpp:120`

## LoadXml
- Description: xml파일에 저장된 내용을 XRSMetaData로 변환한다.
- Declaration: `Source/NXDLrs/XRSFile.h:227`
- Implementation: `Source/NXDLrs/XRSMetaData.cpp:180`

## RemoveKey
- Description: 특정 Key를 삭제한다..
- Declaration: `Source/NXDLrs/XRSFile.h:211`
- Implementation: `Source/NXDLrs/XRSMetaData.cpp:157`

## SaveXml
- Description: XRSMetaData에 저장된 데이터 셋을 xml 파일로 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:220`
- Implementation: `Source/NXDLrs/XRSMetaData.cpp:171`

## SetValue
- Description: 특정 Key에 해당하는 Value값을 설정한다.
- Declaration: `Source/NXDLrs/XRSFile.h:199`, `Source/NXDLrs/XRSFile.h:205`
- Implementation: `Source/NXDLrs/XRSMetaData.cpp:137`, `Source/NXDLrs/XRSMetaData.cpp:142`
