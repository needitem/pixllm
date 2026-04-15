---
title: Pixoneer.NXDL.NNCW.XncwObserver Methods
aliases:
  - XncwObserver Methods
  - Pixoneer.NXDL.NNCW.XncwObserver
  - XncwObserver
symbols:
  - XncwObserver
  - AttachTo
  - GetDistance
  - GetLayerID
  - Initialize
  - SetDistance
  - SetHeading
  - SetState
  - SetTilt
  - SetYawPitchRollOffset
  - SurveyAutoCenter
  - SurveyNone
  - SurveyTargetObj
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nncw
---

# Overview
- Namespace: `Pixoneer.NXDL.NNCW`
- Type: `XncwObserver`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NNCW_XncwObserver.htm`
- Type declaration: `Source/NXDLncw/NXDLncw.h:345`
- Method count: `12`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NNCW.XncwObserver
type_name: XncwObserver
namespace: Pixoneer.NXDL.NNCW
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
## AttachTo
- Description: PlanetView에 레이어를 첨부한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:409`
- Implementation: `Source/NXDLncw/XncwObserver.cpp:52`

## GetDistance
- Description: 대상과 시점 간의 거리를 가져온다.
- Declaration: `Source/NXDLncw/NXDLncw.h:436`
- Implementation: `Source/NXDLncw/XncwObserver.cpp:110`

## GetLayerID
- Description: 레이어 ID를 가져온다. (Overrides NXRenderLayerGetLayerID)
- Declaration: `Source/NXDLncw/NXDLncw.h:400`
- Implementation: `Source/NXDLncw/XncwObserver.cpp:134`

## Initialize
- Description: 내부 초기화 함수. NXPlanetEngine에 의해 자동적으로 호출된다. (Overrides NXRenderLayerInitialize)
- Declaration: `Source/NXDLncw/NXDLncw.h:403`
- Implementation: `Source/NXDLncw/XncwObserver.cpp:42`

## SetDistance
- Description: 대상과 시점 간의 거리를 설정한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:432`
- Implementation: `Source/NXDLncw/XncwObserver.cpp:104`

## SetHeading
- Description: 뷰에 대한 헤딩을 설정한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:446`
- Implementation: `Source/NXDLncw/XncwObserver.cpp:122`

## SetState
- Description: 뷰 모드를 변경한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:428`
- Implementation: `Source/NXDLncw/XncwObserver.cpp:98`

## SetTilt
- Description: 뷰에 대한 기울기를 설정한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:450`
- Implementation: `Source/NXDLncw/XncwObserver.cpp:128`

## SetYawPitchRollOffset
- Description: 뷰 위치를 설정한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:442`
- Implementation: `Source/NXDLncw/XncwObserver.cpp:116`

## SurveyAutoCenter
- Description: 2개 이상의 대상 객체에 대해 자동으로 중심 위치를 기준으로 조망한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:424`
- Implementation: `Source/NXDLncw/XncwObserver.cpp:77`

## SurveyNone
- Description: 뷰 모드를 "Unusable"로 설정하고 카메라를 기본 상태로 설정한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:413`
- Implementation: `Source/NXDLncw/XncwObserver.cpp:64`

## SurveyTargetObj
- Description: 대상 객체를 특정 뷰 모드로 조망한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:419`
- Implementation: `Source/NXDLncw/XncwObserver.cpp:71`
