---
title: Pixoneer.NXDL.NGR.X3DModelDriverManager Methods
aliases:
  - X3DModelDriverManager Methods
  - Pixoneer.NXDL.NGR.X3DModelDriverManager
  - X3DModelDriverManager
symbols:
  - X3DModelDriverManager
  - Convert
  - GetFilters
  - Initialize
  - LoadFile
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - ngr
---

# Overview
- Namespace: `Pixoneer.NXDL.NGR`
- Type: `X3DModelDriverManager`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NGR_X3DModelDriverManager.htm`
- Type declaration: `Source/NXDLgr/X3DModel.h:106`
- Method count: `4`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NGR.X3DModelDriverManager
type_name: X3DModelDriverManager
namespace: Pixoneer.NXDL.NGR
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
## Convert
- Description: 3D 모델의 포맷 및 정점의 좌표계를 변환한다.
- Declaration: `Source/NXDLgr/X3DModel.h:177`
- Implementation: `Source/NXDLgr/X3DModelDriverManager.cpp:90`

## GetFilters
- Description: 열기 대화상자 등에서 사용할 수 있는 형식 필터를 반환한다.
- Declaration: `Source/NXDLgr/X3DModel.h:181`
- Implementation: `Source/NXDLgr/X3DModelDriverManager.cpp:111`

## Initialize
- Description: 객체의 초기화를 수행한다. 초기화시 파일로딩을 위한 각종 Resource를 로딩한다.
- Declaration: `Source/NXDLgr/X3DModel.h:121`
- Implementation: `Source/NXDLgr/X3DModelDriverManager.cpp:41`

## LoadFile
- Description: 입력 파일 경로를 읽어 X3DModel 객체를 생성한다.
- Declaration: `Source/NXDLgr/X3DModel.h:127`, `Source/NXDLgr/X3DModel.h:137`
- Implementation: `Source/NXDLgr/X3DModelDriverManager.cpp:53`, `Source/NXDLgr/X3DModelDriverManager.cpp:72`
