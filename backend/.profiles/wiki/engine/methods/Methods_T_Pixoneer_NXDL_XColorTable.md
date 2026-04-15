---
title: Pixoneer.NXDL.XColorTable Methods
aliases:
  - XColorTable Methods
  - Pixoneer.NXDL.XColorTable
  - XColorTable
symbols:
  - XColorTable
  - GetCLT
  - GetPaletteNameList
  - Load
  - LoadColorTable
  - Save
  - SetCLT
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `XColorTable`
- HTML source: `html/Methods_T_Pixoneer_NXDL_XColorTable.htm`
- Type declaration: `Source/NXDL/NXDL.h:2800`
- Method count: `6`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.XColorTable
type_name: XColorTable
namespace: Pixoneer.NXDL
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
## GetCLT
- Description: 특정 인덱스에 해당하는 칼라 값을 얻는다.
- Declaration: `Source/NXDL/NXDL.h:2833`
- Implementation: `Source/NXDL/XColorTable.cpp:71`

## GetPaletteNameList
- Description: 칼라 테이블의 ID에 해당하는 이름 리스트를 얻는다. 인덱스 ID와 String Array상의 순서가 일치한다.
- Declaration: `Source/NXDL/NXDL.h:2849`
- Implementation: `Source/NXDL/XColorTable.cpp:188`

## Load
- Description: 바이너리 데이터로 저장된 칼라 테이블 정보를 로딩한다.
- Declaration: `Source/NXDL/NXDL.h:2839`
- Implementation: `Source/NXDL/XColorTable.cpp:86`

## LoadColorTable
- Description: eColorTable에 정의된 ColorTable ID를 이용하여 Color Table을 설정한다.
- Declaration: `Source/NXDL/NXDL.h:2812`
- Implementation: `Source/NXDL/XColorTable.cpp:39`

## Save
- Description: 칼라 테이블 정보를 바이너리 데이터로 저장한다.
- Declaration: `Source/NXDL/NXDL.h:2845`
- Implementation: `Source/NXDL/XColorTable.cpp:136`

## SetCLT
- Description: 특정 인덱스값에 특정 칼라 값을 설정한다.
- Declaration: `Source/NXDL/NXDL.h:2817`, `Source/NXDL/NXDL.h:2824`
- Implementation: `Source/NXDL/XColorTable.cpp:53`, `Source/NXDL/XColorTable.cpp:62`
