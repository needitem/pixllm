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
  - use_this_page_only_after_a_workflow_or_type_hint_narrows_scope
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page only as a verification layer after a workflow or explicit type hint identifies the target type.
- Cross-check declaration and implementation lines when overloads, properties, or call shapes matter.
- Do not synthesize end-to-end usage answers from this page alone.
## GetResultAltitude
- Description: 3D의 경우 중점과 끝점 간의 고도차이를 반환한다. 단위는 meter. 유효하지 않은 경우 MAX_REAL64를 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2908`
- Implementation: `Source/NXDLscene/XscMeasureRelation.cpp:88`

## GetResultDistance
- Description: 중점과 끝점 사이의 거리를 반환한다. 단위는 meter. 유효하지 않은 경우 MAX_REAL64를 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2905`
- Implementation: `Source/NXDLscene/XscMeasureRelation.cpp:69`
