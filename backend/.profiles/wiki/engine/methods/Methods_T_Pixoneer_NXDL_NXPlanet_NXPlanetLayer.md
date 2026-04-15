---
title: Pixoneer.NXDL.NXPlanet.NXPlanetLayer Methods
aliases:
  - NXPlanetLayer Methods
  - Pixoneer.NXDL.NXPlanet.NXPlanetLayer
  - NXPlanetLayer
symbols:
  - NXPlanetLayer
  - GetLayerID
  - Initialize
  - ProcessScreenToWorldConvLevel
  - ScreenToWorld
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nxplanet
---

# Overview
- Namespace: `Pixoneer.NXDL.NXPlanet`
- Type: `NXPlanetLayer`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXPlanet_NXPlanetLayer.htm`
- Type declaration: `Source/NXPlanet/NXPlanetLayer.h:164`
- Method count: `4`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXPlanet.NXPlanetLayer
type_name: NXPlanetLayer
namespace: Pixoneer.NXDL.NXPlanet
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
## GetLayerID
- Description: 레이어의 고유 ID를 가져온다.(Overrides NXRenderLayerGetLayerID)
- Declaration: `Source/NXPlanet/NXPlanetLayer.h:176`
- Implementation: `Source/NXPlanet/NXPlanetLayer.cpp:213`

## Initialize
- Description: 내부 초기화 함수이다. 이것은 NXPlanetEngine에 의해 오직 한번 호출 된다. (Overrides NXRenderLayerInitialize)
- Declaration: `Source/NXPlanet/NXPlanetLayer.h:179`
- Implementation: `Source/NXPlanet/NXPlanetLayer.cpp:74`

## ProcessScreenToWorldConvLevel
- Description: 사용자가 ScreenToWorld 함수를 호출할 때 처리 수준을 제어하는 고급 함수이다.
- Declaration: `Source/NXPlanet/NXPlanetLayer.h:203`
- Implementation: `Source/NXPlanet/NXPlanetLayer.cpp:170`

## ScreenToWorld
- Description: 스크린 좌표를 세계 좌표로 변환하며, 한 점을 입력으로 한다.
- Declaration: `Source/NXPlanet/NXPlanetLayer.h:210`, `Source/NXPlanet/NXPlanetLayer.h:217`
- Implementation: `Source/NXPlanet/NXPlanetLayer.cpp:182`, `Source/NXPlanet/NXPlanetLayer.cpp:190`
