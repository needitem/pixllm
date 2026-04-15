---
title: Pixoneer.NXDL.NIO.XVectorIO Methods
aliases:
  - XVectorIO Methods
  - Pixoneer.NXDL.NIO.XVectorIO
  - XVectorIO
symbols:
  - XVectorIO
  - Export
  - GetDriverKey
  - GetFileInfo
  - GetFiltersForLoad
  - GetFiltersForSave
  - Initialize
  - IsExtensionExportSupported
  - IsExtensionImportSupported
  - IsKeyImportSupported
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
- Type: `XVectorIO`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NIO_XVectorIO.htm`
- Type declaration: `Source/NXDLio/NXDLio.h:791`
- Method count: `10`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NIO.XVectorIO
type_name: XVectorIO
namespace: Pixoneer.NXDL.NIO
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
## Export
- Description: 표준 및 상용 포맷의 벡터 파일로 저장한다.
- Declaration: `Source/NXDLio/NXDLio.h:906`
- Implementation: `Source/NXDLio/XVectorIO.cpp:241`

## GetDriverKey
- Description: 입력 인덱스에 의한 드라이버 파일 키워드를 반환한다.
- Declaration: `Source/NXDLio/NXDLio.h:920`
- Implementation: `Source/NXDLio/XVectorIO.cpp:330`

## GetFileInfo
- Description: 표준 및 상용 포맷의 벡터 파일 정보를 로딩한다.
- Declaration: `Source/NXDLio/NXDLio.h:865`, `Source/NXDLio/NXDLio.h:880`, `Source/NXDLio/NXDLio.h:896`
- Implementation: `Source/NXDLio/XVectorIO.cpp:99`, `Source/NXDLio/XVectorIO.cpp:128`, `Source/NXDLio/XVectorIO.cpp:183`

## GetFiltersForLoad
- Description: XVectorIO객체로부터 로딩이 가능한 필터를 얻는다. 이 필터 문자열은 열기 대화상자 등에서 사용할 수 있다.
- Declaration: `Source/NXDLio/NXDLio.h:909`
- Implementation: `Source/NXDLio/XVectorIO.cpp:266`

## GetFiltersForSave
- Description: XVectorIO객체로부터 저장이 가능한 필터를 얻는다. 이 필터 문자열은 저장 대화상자 등에서 사용할 수 있다.
- Declaration: `Source/NXDLio/NXDLio.h:914`
- Implementation: `Source/NXDLio/XVectorIO.cpp:296`

## Initialize
- Description: 객체를 초기화하고 벡터 드라이버를 로딩한다.
- Declaration: `Source/NXDLio/NXDLio.h:802`
- Implementation: `Source/NXDLio/XVectorIO.cpp:34`

## IsExtensionExportSupported
- Description: 출력(export) 기능에 특정 파일 형식을 지원하는지 확인한다.
- Declaration: `Source/NXDLio/NXDLio.h:812`
- Implementation: `Source/NXDLio/XVectorIO.cpp:69`

## IsExtensionImportSupported
- Description: 입력(import) 기능에 특정 파일 형식을 지원하는지 확인한다.
- Declaration: `Source/NXDLio/NXDLio.h:807`
- Implementation: `Source/NXDLio/XVectorIO.cpp:54`

## IsKeyImportSupported
- Description: 입력 기능에 특정 파일 형식을 지원하는지 확인한다.
- Declaration: `Source/NXDLio/NXDLio.h:817`
- Implementation: `Source/NXDLio/XVectorIO.cpp:84`

## LoadFile
- Description: 표준 및 상용 포맷의 벡터 파일을 로딩한다.
- Declaration: `Source/NXDLio/NXDLio.h:824`, `Source/NXDLio/NXDLio.h:834`, `Source/NXDLio/NXDLio.h:842`, `Source/NXDLio/NXDLio.h:853`
- Implementation: `Source/NXDLio/XVectorIO.cpp:189`, `Source/NXDLio/XVectorIO.cpp:195`, `Source/NXDLio/XVectorIO.cpp:231`, `Source/NXDLio/XVectorIO.cpp:236`
