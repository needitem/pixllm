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
  - use_this_page_only_after_a_workflow_or_type_hint_narrows_scope
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page only as a verification layer after a workflow or explicit type hint identifies the target type.
- Cross-check declaration and implementation lines when overloads, properties, or call shapes matter.
- Do not synthesize end-to-end usage answers from this page alone.
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
