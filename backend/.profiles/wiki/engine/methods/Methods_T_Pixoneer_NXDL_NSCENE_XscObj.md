---
title: Pixoneer.NXDL.NSCENE.XscObj Methods
aliases:
  - XscObj Methods
  - Pixoneer.NXDL.NSCENE.XscObj
  - XscObj
symbols:
  - XscObj
  - Dispose
  - Draw
  - GetPropertyNameAt
  - GetPropertyValueAt
  - GetTypeName
  - HitTest
  - OrthoDraw
  - SetRange
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nscene
---

# Overview
- Namespace: `Pixoneer.NXDL.NSCENE`
- Type: `XscObj`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSCENE_XscObj.htm`
- Type declaration: `Source/NXDLscene/NXDLscene.h:241`
- Method count: `8`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSCENE.XscObj
type_name: XscObj
namespace: Pixoneer.NXDL.NSCENE
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
## Dispose
- Description: No description in HTML reference.
- Declaration: `not found`
- Implementation: `not found`

## Draw
- Description: 객체를 그린다, 이것은 반드시 랜더 스레드에서 실행해야 한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:312`
- Implementation: `Source/NXDLscene/XscObj.cpp:207`

## GetPropertyNameAt
- Description: 입력 인덱스에 대응하는 객체 속성 이름(필드 이름)을 가져온다.
- Declaration: `Source/NXDLscene/NXDLscene.h:370`
- Implementation: `Source/NXDLscene/XscObj.cpp:570`

## GetPropertyValueAt
- Description: 입력 인덱스에 대응하는 객체 속성값을 가져온다.
- Declaration: `Source/NXDLscene/NXDLscene.h:365`
- Implementation: `Source/NXDLscene/XscObj.cpp:551`

## GetTypeName
- Description: 객체 유형의 이름을 가져온다.
- Declaration: `Source/NXDLscene/NXDLscene.h:295`
- Implementation: `Source/NXDLscene/XscObj.cpp:159`

## HitTest
- Description: 특정 좌표에 대한 객치의 Hit-testing을 수행한다. 이 함수의 경우, 테스팅 버퍼를 0으로 하여 수행하기 때문에 특정좌표에 객체가 정확하게 위치해야 true를 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:281`, `Source/NXDLscene/NXDLscene.h:291`
- Implementation: `Source/NXDLscene/XscObj.cpp:97`, `Source/NXDLscene/XscObj.cpp:128`

## OrthoDraw
- Description: 객체를 정사투영법(orthographic mode)으로 그린다. 이것은 반드시 랜더 스레드에서 실행해야 한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:318`
- Implementation: `Source/NXDLscene/XscObj.cpp:224`

## SetRange
- Description: 객체의 둘러싼 경계 범위를 설정한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:306`
- Implementation: `Source/NXDLscene/XscObj.cpp:191`
