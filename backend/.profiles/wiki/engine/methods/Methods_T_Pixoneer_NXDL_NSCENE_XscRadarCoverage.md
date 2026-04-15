---
title: Pixoneer.NXDL.NSCENE.XscRadarCoverage Methods
aliases:
  - XscRadarCoverage Methods
  - Pixoneer.NXDL.NSCENE.XscRadarCoverage
  - XscRadarCoverage
symbols:
  - XscRadarCoverage
  - AddCoverageData
  - AddMajorColor
  - GetNumberOfSection
  - GetPoint
  - RemoveAllCoverageData
  - RemoveAllMajorColor
  - SetMinorColor
  - SetPoint
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
- Type: `XscRadarCoverage`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSCENE_XscRadarCoverage.htm`
- Type declaration: `Source/NXDLscene/NXDLscene.h:1089`
- Method count: `8`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSCENE.XscRadarCoverage
type_name: XscRadarCoverage
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
## AddCoverageData
- Description: 레이더 커버리지 데이터를 추가한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:1138`
- Implementation: `Source/NXDLscene/XscRadarCoverage.cpp:523`

## AddMajorColor
- Description: 레이더 커버리지 도시 주 색상을 추가한다. 첫번째 추가되는 색상으로 최신 레이더 커버리지 데이터를 도시한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:1124`
- Implementation: `Source/NXDLscene/XscRadarCoverage.cpp:477`

## GetNumberOfSection
- Description: 레이더 커버리지 부분의 개수를 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:1145`
- Implementation: `Source/NXDLscene/XscRadarCoverage.cpp:509`

## GetPoint
- Description: 레이더의 중앙 위치를 확인한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:1111`, `Source/NXDLscene/NXDLscene.h:1120`
- Implementation: `Source/NXDLscene/XscRadarCoverage.cpp:172`, `Source/NXDLscene/XscRadarCoverage.cpp:209`

## RemoveAllCoverageData
- Description: 레이더 커버리지 데이터를 모두 삭제한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:1141`
- Implementation: `Source/NXDLscene/XscRadarCoverage.cpp:537`

## RemoveAllMajorColor
- Description: 추가된 레이더 커버리지 도시 주 색상을 모두 삭제한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:1131`
- Implementation: `Source/NXDLscene/XscRadarCoverage.cpp:550`

## SetMinorColor
- Description: 레이더 커버리지 도시 부 색상을 설정한다. 추가한 레이더 커버리지 데이터 개수가 주 색상보다 많아지면 부 색상으로 도시한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:1128`
- Implementation: `Source/NXDLscene/XscRadarCoverage.cpp:493`

## SetPoint
- Description: 레이더의 중앙 위치를 설정한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:1104`, `Source/NXDLscene/NXDLscene.h:1116`
- Implementation: `Source/NXDLscene/XscRadarCoverage.cpp:158`, `Source/NXDLscene/XscRadarCoverage.cpp:195`
