---
title: Pixoneer.NXDL.NSCENE.XscMeasureAngleBase Methods
aliases:
  - XscMeasureAngleBase Methods
  - Pixoneer.NXDL.NSCENE.XscMeasureAngleBase
  - XscMeasureAngleBase
symbols:
  - XscMeasureAngleBase
  - GetCenter
  - GetEnd
  - GetResultAngle
  - SetCenter
  - SetEnd
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
- Type: `XscMeasureAngleBase`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSCENE_XscMeasureAngleBase.htm`
- Type declaration: `Source/NXDLscene/NXDLscene.h:2734`
- Method count: `5`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSCENE.XscMeasureAngleBase
type_name: XscMeasureAngleBase
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
## GetCenter
- Description: 각도를 이루는 3개의 정점 중 중점을 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2770`, `Source/NXDLscene/NXDLscene.h:2780`
- Implementation: `Source/NXDLscene/XscMeasureAngle.cpp:99`, `Source/NXDLscene/XscMeasureAngle.cpp:135`

## GetEnd
- Description: 각도를 이루는 3개의 정점 중 끝점을 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2776`, `Source/NXDLscene/NXDLscene.h:2784`
- Implementation: `Source/NXDLscene/XscMeasureAngle.cpp:117`, `Source/NXDLscene/XscMeasureAngle.cpp:152`

## GetResultAngle
- Description: 각도 측정 결과 중 각도를 확인한다. 단위는 degree. 유효하지 않으면 MAX_REAL64를 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2820`
- Implementation: `Source/NXDLscene/XscMeasureAngle.cpp:169`, `Source/NXDLscene/XscMeasureAzimuth.cpp:44`

## SetCenter
- Description: 각도를 이루는 3개의 정점 중 중점을 설정한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2749`, `Source/NXDLscene/NXDLscene.h:2759`
- Implementation: `Source/NXDLscene/XscMeasureAngle.cpp:40`, `Source/NXDLscene/XscMeasureAngle.cpp:68`

## SetEnd
- Description: 각도를 이루는 3개의 정점 중 끝점을 설정한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2755`, `Source/NXDLscene/NXDLscene.h:2763`
- Implementation: `Source/NXDLscene/XscMeasureAngle.cpp:54`, `Source/NXDLscene/XscMeasureAngle.cpp:84`
