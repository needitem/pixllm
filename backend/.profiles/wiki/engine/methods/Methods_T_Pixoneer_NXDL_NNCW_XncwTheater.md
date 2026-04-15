---
title: Pixoneer.NXDL.NNCW.XncwTheater Methods
aliases:
  - XncwTheater Methods
  - Pixoneer.NXDL.NNCW.XncwTheater
  - XncwTheater
symbols:
  - XncwTheater
  - AddEquipment
  - AttachTo
  - FixObjectDrawSize
  - FreeEquipment
  - GetEquipment
  - GetLayerID
  - Initialize
  - Pick
  - ShowAllObjects
  - UpdateVisibleArea
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
- Type: `XncwTheater`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NNCW_XncwTheater.htm`
- Type declaration: `Source/NXDLncw/NXDLncw.h:99`
- Method count: `10`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NNCW.XncwTheater
type_name: XncwTheater
namespace: Pixoneer.NXDL.NNCW
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
## AddEquipment
- Description: Theater에 장비 객체를 추가한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:142`
- Implementation: `Source/NXDLncw/XncwTheater.cpp:89`

## AttachTo
- Description: PlanetView에 레이어를 첨부한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:131`
- Implementation: `Source/NXDLncw/XncwTheater.cpp:44`

## FixObjectDrawSize
- Description: 대상 뷰에 도시할 때 장비 크기를 고정한다. Algor : distance(eye,objPos) * scaleFactor * objectSize scaleFactor sample: 0.0002
- Declaration: `Source/NXDLncw/NXDLncw.h:167`
- Implementation: `Source/NXDLncw/XncwTheater.cpp:125`

## FreeEquipment
- Description: Theater에서 ID에 따른 장비 객체를 해제한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:147`
- Implementation: `Source/NXDLncw/XncwTheater.cpp:103`

## GetEquipment
- Description: Theater에서 ID에 따른 장비(equipment) 객체를 가져온다.
- Declaration: `Source/NXDLncw/NXDLncw.h:136`
- Implementation: `Source/NXDLncw/XncwTheater.cpp:72`

## GetLayerID
- Description: 레이어 ID를 가져온다. (Overrides NXRenderLayerGetLayerID)
- Declaration: `Source/NXDLncw/NXDLncw.h:119`
- Implementation: `Source/NXDLncw/XncwTheater.cpp:156`

## Initialize
- Description: 내부 초기화 함수. NXPlanetEngine이 자동 호출한다. (Overrides NXRenderLayerInitialize)
- Declaration: `Source/NXDLncw/NXDLncw.h:122`
- Implementation: `Source/NXDLncw/XncwTheater.cpp:56`

## Pick
- Description: 대상 장비 객체를 선택하도록 선택(pick) 명령을 보낸다.
- Declaration: `Source/NXDLncw/NXDLncw.h:173`
- Implementation: `Source/NXDLncw/XncwTheater.cpp:132`

## ShowAllObjects
- Description: 대상 view에서 모든 장비 객체를 보이거나 숨기도록 한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:157`
- Implementation: `Source/NXDLncw/XncwTheater.cpp:118`

## UpdateVisibleArea
- Description: 사용자에 의해 theater 구성이 변경되면 theater의 영역을 갱신할 수 있도록 호출한다.
- Declaration: `Source/NXDLncw/NXDLncw.h:151`
- Implementation: `Source/NXDLncw/XncwTheater.cpp:112`
