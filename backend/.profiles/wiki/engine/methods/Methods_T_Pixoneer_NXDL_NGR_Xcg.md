---
title: Pixoneer.NXDL.NGR.Xcg Methods
aliases:
  - Xcg Methods
  - Pixoneer.NXDL.NGR.Xcg
  - Xcg
symbols:
  - Xcg
  - GetClosestPtOnLine
  - GetClosestPtOnLineSegment
  - GetDistPtToLine
  - GetDistPtToLineSegment
  - IsPtInPoly
  - IsPtOnPoly
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
- Type: `Xcg`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NGR_Xcg.htm`
- Type declaration: `Source/NXDLgr/NXDLgr.h:4114`
- Method count: `6`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NGR.Xcg
type_name: Xcg
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
## GetClosestPtOnLine
- Description: 직선과 점의 최단점을 구한다.
- Declaration: `Source/NXDLgr/NXDLgr.h:4133`
- Implementation: `Source/NXDLgr/NXDLgr.cpp:468`, `Source/NXDLgr/NXDLgr.cpp:476`

## GetClosestPtOnLineSegment
- Description: 선분과 점의 최단점을 구한다.
- Declaration: `Source/NXDLgr/NXDLgr.h:4142`
- Implementation: `Source/NXDLgr/NXDLgr.cpp:487`, `Source/NXDLgr/NXDLgr.cpp:495`, `Source/NXDLMilSymbol/reference/DrawOverItem.cpp:85`

## GetDistPtToLine
- Description: 직선과 점의 최단거리을 구한다.
- Declaration: `Source/NXDLgr/NXDLgr.h:4151`
- Implementation: `Source/NXDLgr/NXDLgr.cpp:507`, `Source/NXDLgr/NXDLgr.cpp:513`

## GetDistPtToLineSegment
- Description: 선분과 점의 최단점을 구한다.
- Declaration: `Source/NXDLgr/NXDLgr.h:4160`
- Implementation: `Source/NXDLgr/NXDLgr.cpp:522`, `Source/NXDLgr/NXDLgr.cpp:528`

## IsPtInPoly
- Description: 입력 정점배열로 이루어진 2차원 다각형에 대해, 특정 위치의 점이 다각형 내부에 존재하는지 확인한다.
- Declaration: `Source/NXDLgr/NXDLgr.h:4167`
- Implementation: `Source/NXDLgr/NXDLgr.cpp:537`

## IsPtOnPoly
- Description: 입력 정점배열로 이루어진 폴리라인(또는 폴리곤)에 대해 특정 위치에 대한 hit-testing을 수행한다.
- Declaration: `Source/NXDLgr/NXDLgr.h:4124`
- Implementation: `Source/NXDLgr/NXDLgr.cpp:438`, `Source/NXDLgr/NXDLgr.cpp:459`
