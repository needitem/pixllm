---
title: Pixoneer.NXDL.NSCENE.XscMeasureRelation Methods
aliases:
  - XscMeasureRelation Methods
  - Pixoneer.NXDL.NSCENE.XscMeasureRelation
  - XscMeasureRelation
symbols:
  - XscMeasureRelation
  - GetResultAltitude
  - GetResultDistance
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
- Type: `XscMeasureRelation`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSCENE_XscMeasureRelation.htm`
- Type declaration: `Source/NXDLscene/NXDLscene.h:2894`
- Method count: `2`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSCENE.XscMeasureRelation
type_name: XscMeasureRelation
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
## GetResultAltitude
- Description: 3D의 경우 중점과 끝점 간의 고도차이를 반환한다. 단위는 meter. 유효하지 않은 경우 MAX_REAL64를 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2908`
- Implementation: `Source/NXDLscene/XscMeasureRelation.cpp:88`

## GetResultDistance
- Description: 중점과 끝점 사이의 거리를 반환한다. 단위는 meter. 유효하지 않은 경우 MAX_REAL64를 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2905`
- Implementation: `Source/NXDLscene/XscMeasureRelation.cpp:69`
