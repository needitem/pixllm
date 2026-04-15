---
title: Pixoneer.NXDL.NSM.XFrameSensor Methods
aliases:
  - XFrameSensor Methods
  - Pixoneer.NXDL.NSM.XFrameSensor
  - XFrameSensor
symbols:
  - XFrameSensor
  - CalcBound
  - GetModelParams
  - ImageToWorldDistE
  - ImageToWorldDistG
  - Init
  - IsValid
  - SetParamsEarth
  - SetParamsLocal
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nsm
---

# Overview
- Namespace: `Pixoneer.NXDL.NSM`
- Type: `XFrameSensor`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSM_XFrameSensor.htm`
- Type declaration: `Source/NXDLsm/NXDLsm.h:246`
- Method count: `8`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSM.XFrameSensor
type_name: XFrameSensor
namespace: Pixoneer.NXDL.NSM
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
## CalcBound
- Description: 센서 모델을 통해 영상이 촬영될 지리 좌표 영역을 얻는다.
- Declaration: `Source/NXDLsm/NXDLsm.h:285`
- Implementation: `Source/NXDLsm/XFrameSensor.cpp:171`

## GetModelParams
- Description: 설정된 센서 모델 파라미터를 얻는다.
- Declaration: `Source/NXDLsm/NXDLsm.h:277`
- Implementation: `Source/NXDLsm/XFrameSensor.cpp:166`

## ImageToWorldDistE
- Description: 대상점의 이미지 좌표와 센서로부터 거리를 입력 받아 대상점의 직교 좌표(지역 또는 ECEF 좌표)를 구한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:292`
- Implementation: `Source/NXDLsm/XFrameSensor.cpp:222`

## ImageToWorldDistG
- Description: 대상점의 이미지 좌표와 센서로부터 거리를 입력 받아 대상점의 위경도 좌표를 구한다. 지역 모드인 경우 직교 좌표점을 그대로 반환한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:299`
- Implementation: `Source/NXDLsm/XFrameSensor.cpp:235`

## Init
- Description: 파라미터를 초기화한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:259`
- Implementation: `Source/NXDLsm/XFrameSensor.cpp:85`

## IsValid
- Description: 입력된 파라미터가 유효한지 판단한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:263`
- Implementation: `Source/NXDLsm/XFrameSensor.cpp:129`

## SetParamsEarth
- Description: 지구좌표 시스템 센서 모델 파라미터를 설정한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:268`
- Implementation: `Source/NXDLsm/XFrameSensor.cpp:134`

## SetParamsLocal
- Description: 로컬 좌표 시스템 센서 모델 파라미터 설정
- Declaration: `Source/NXDLsm/NXDLsm.h:273`
- Implementation: `Source/NXDLsm/XFrameSensor.cpp:150`
