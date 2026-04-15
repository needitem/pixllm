---
title: Pixoneer.NXDL.NEQUIP.XEquipObj Methods
aliases:
  - XEquipObj Methods
  - Pixoneer.NXDL.NEQUIP.XEquipObj
  - XEquipObj
symbols:
  - XEquipObj
  - DrawBefore
  - DrawOver
  - HideObject
  - IsHiddenObject
  - OrthoRender
  - SetBoundingBoxProperty
  - SetGroundLevelRange
  - SetPosition
  - SetStates
  - SetYawPitchRoll
  - ShowBoundingBox
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nequip
---

# Overview
- Namespace: `Pixoneer.NXDL.NEQUIP`
- Type: `XEquipObj`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NEQUIP_XEquipObj.htm`
- Type declaration: `Source/NXDLncw/NXDLequip.h:34`
- Method count: `11`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NEQUIP.XEquipObj
type_name: XEquipObj
namespace: Pixoneer.NXDL.NEQUIP
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
## DrawBefore
- Description: Overridable function. 객체에 그려지기 전에 엔진이 호출한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:140`, `Source/NXDLncw/NXDLequip.h:158`
- Implementation: `Source/NXDLncw/XEquipObj.cpp:104`, `Source/NXDLncw/XEquipObj.cpp:119`

## DrawOver
- Description: Overridable function. 객체에 그려진 후에 엔진이 호출한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:146`, `Source/NXDLncw/NXDLequip.h:164`
- Implementation: `Source/NXDLncw/XEquipObj.cpp:109`, `Source/NXDLncw/XEquipObj.cpp:124`

## HideObject
- Description: 객체를 숨긴다.
- Declaration: `Source/NXDLncw/NXDLequip.h:104`
- Implementation: `Source/NXDLncw/XEquipObj.cpp:92`

## IsHiddenObject
- Description: 객체가 숨겨져 있는지 확인한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:108`
- Implementation: `Source/NXDLncw/XEquipObj.cpp:98`

## OrthoRender
- Description: Overridable function. 객체에 그려진 후에 엔진이 호출한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:152`
- Implementation: `Source/NXDLncw/XEquipObj.cpp:114`

## SetBoundingBoxProperty
- Description: 장비 경계 영역을 그리는 도시 속성을 설정한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:99`
- Implementation: `Source/NXDLncw/XEquipObj.cpp:86`

## SetGroundLevelRange
- Description: 지상 객체의 표고 탐색 범위를 지정한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:175`
- Implementation: `Source/NXDLncw/XEquipObj.cpp:247`

## SetPosition
- Description: 위경도 좌표 형식의 장비 위치를 설정한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:77`, `Source/NXDLncw/NXDLequip.h:82`
- Implementation: `Source/NXDLncw/XEquipObj.cpp:59`, `Source/NXDLncw/XEquipObj.cpp:66`

## SetStates
- Description: 위경도 좌표 형식의 장비 상태(equipment state)를 설정한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:66`, `Source/NXDLncw/NXDLequip.h:72`
- Implementation: `Source/NXDLncw/XEquipObj.cpp:44`, `Source/NXDLncw/XEquipObj.cpp:51`

## SetYawPitchRoll
- Description: 장비 자세(equipment attitude)를 설정한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:89`
- Implementation: `Source/NXDLncw/XEquipObj.cpp:73`

## ShowBoundingBox
- Description: 장비의 경계 영역 상자 도시여부를 설정한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:94`
- Implementation: `Source/NXDLncw/XEquipObj.cpp:79`
