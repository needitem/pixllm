---
title: Pixoneer.NXDL.NRS.XDMBandGeoCorrect Methods
aliases:
  - XDMBandGeoCorrect Methods
  - Pixoneer.NXDL.NRS.XDMBandGeoCorrect
  - XDMBandGeoCorrect
symbols:
  - XDMBandGeoCorrect
  - CalcSourcePixelBound
  - GetInputParam
  - SetInputParam
  - WarpPointImage2Map
  - WarpPointMap2Image
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
- Type: `XDMBandGeoCorrect`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XDMBandGeoCorrect.htm`
- Type declaration: `Source/NXDLrs/XDMBandGeoCorrect.h:162`
- Method count: `5`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XDMBandGeoCorrect
type_name: XDMBandGeoCorrect
namespace: Pixoneer.NXDL.NRS
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
## CalcSourcePixelBound
- Description: 파라미터로 입력된 XGCPSets객체로부터 Map to Image변환 관계를 이용하여 지리좌표로 부터 이미지 좌표계로 변환시킨다.
- Declaration: `Source/NXDLrs/XDMBandGeoCorrect.h:195`
- Implementation: `Source/NXDLrs/XDMBandGeoCorrect.cpp:128`

## GetInputParam
- Description: 기하보정 수행을 위한 입력 파라미터를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandGeoCorrect.h:183`
- Implementation: `Source/NXDLrs/XDMBandGeoCorrect.cpp:123`

## SetInputParam
- Description: 기하보정을 위한 입력 파라미터를 설정한다.
- Declaration: `Source/NXDLrs/XDMBandGeoCorrect.h:178`
- Implementation: `Source/NXDLrs/XDMBandGeoCorrect.cpp:78`

## WarpPointImage2Map
- Description: 파라미터로 입력된 XGCPSets객체로부터 Image to Map변환 관계를 이용하여 이미지좌표를 지리 좌표로 변환시킨다.
- Declaration: `Source/NXDLrs/XDMBandGeoCorrect.h:213`
- Implementation: `Source/NXDLrs/XDMBandGeoCorrect.cpp:150`

## WarpPointMap2Image
- Description: 파라미터로 입력된 XGCPSets객체로부터 Map to Image변환 관계를 이용하여 지리좌표를 이미지 좌표로 변환시킨다.
- Declaration: `Source/NXDLrs/XDMBandGeoCorrect.h:204`
- Implementation: `Source/NXDLrs/XDMBandGeoCorrect.cpp:139`
