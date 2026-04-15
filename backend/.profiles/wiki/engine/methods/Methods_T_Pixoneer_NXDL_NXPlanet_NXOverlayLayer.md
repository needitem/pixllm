---
title: Pixoneer.NXDL.NXPlanet.NXOverlayLayer Methods
aliases:
  - NXOverlayLayer Methods
  - Pixoneer.NXDL.NXPlanet.NXOverlayLayer
  - NXOverlayLayer
symbols:
  - NXOverlayLayer
  - AddCompMan
  - AddComposite
  - GetCompMan
  - GetComposite
  - Move
  - MoveBottom
  - MoveDown
  - MoveTop
  - MoveUp
  - Remove
  - SetAlpha
  - SetRenderLayer
  - SetTransparentValue
  - UpdateCompMan
  - UpdateComposite
  - UpdateSource
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
- Type: `NXOverlayLayer`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXPlanet_NXOverlayLayer.htm`
- Type declaration: `Source/NXPlanet/NXOverlay.h:75`
- Method count: `16`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXPlanet.NXOverlayLayer
type_name: NXOverlayLayer
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
## AddCompMan
- Description: composite 매니저를 추가한다. 도시레벨은 입력 데이터의 영역을 기반으로 자동으로 설정된다.
- Declaration: `Source/NXPlanet/NXOverlay.h:102`, `Source/NXPlanet/NXOverlay.h:110`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:102`, `Source/NXPlanet/NXOverlay.cpp:125`

## AddComposite
- Description: composite를 추가한다. 도시레벨은 입력 데이터의 영역을 기반으로 자동으로 설정된다.
- Declaration: `Source/NXPlanet/NXOverlay.h:116`, `Source/NXPlanet/NXOverlay.h:124`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:130`, `Source/NXPlanet/NXOverlay.cpp:153`

## GetCompMan
- Description: AddCompMan 함수를 통해 추가된 composite 메니저를 가져온다.
- Declaration: `Source/NXPlanet/NXOverlay.h:143`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:292`

## GetComposite
- Description: AddComposite 함수를 통해 추가된 composite를 가져온다.
- Declaration: `Source/NXPlanet/NXOverlay.h:138`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:270`

## Move
- Description: composite를 이동한다.
- Declaration: `Source/NXPlanet/NXOverlay.h:186`, `Source/NXPlanet/NXOverlay.h:192`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:346`, `Source/NXPlanet/NXOverlay.cpp:358`

## MoveBottom
- Description: 하단으로 이동한다.
- Declaration: `Source/NXPlanet/NXOverlay.h:227`, `Source/NXPlanet/NXOverlay.h:232`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:459`, `Source/NXPlanet/NXOverlay.cpp:470`

## MoveDown
- Description: 아래로 이동한다.
- Declaration: `Source/NXPlanet/NXOverlay.h:207`, `Source/NXPlanet/NXOverlay.h:212`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:403`, `Source/NXPlanet/NXOverlay.cpp:414`

## MoveTop
- Description: 상단으로 이동한다.
- Declaration: `Source/NXPlanet/NXOverlay.h:217`, `Source/NXPlanet/NXOverlay.h:222`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:431`, `Source/NXPlanet/NXOverlay.cpp:442`

## MoveUp
- Description: 위로 이동한다.
- Declaration: `Source/NXPlanet/NXOverlay.h:197`, `Source/NXPlanet/NXOverlay.h:202`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:375`, `Source/NXPlanet/NXOverlay.cpp:386`

## Remove
- Description: 인덱스에 해당하는 composite 또는 composite 매니저를 삭제한다.
- Declaration: `Source/NXPlanet/NXOverlay.h:162`, `Source/NXPlanet/NXOverlay.h:167`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:314`, `Source/NXPlanet/NXOverlay.cpp:329`

## SetAlpha
- Description: 투명도를 설정한다.
- Declaration: `Source/NXPlanet/NXOverlay.h:172`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:181`

## SetRenderLayer
- Description: RenderLayer의 렌더링 결과를 배경지도와 같이 렌더링될 수 있도록 설정한다. 프로그램을 종료할 때 NXOverlay에서 해당 레이어를 삭제(NXOverlay.Remove(0))하고 NXRenderLayer의 dispose를 호출해야 한다.
- Declaration: `Source/NXPlanet/NXOverlay.h:133`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:158`

## SetTransparentValue
- Description: 투명값(null 처리)을 설정한다.
- Declaration: `Source/NXPlanet/NXOverlay.h:180`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:199`

## UpdateCompMan
- Description: 추가할 때 지정한 Composite Manager를 찾아 갱신한다.
- Declaration: `Source/NXPlanet/NXOverlay.h:153`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:251`

## UpdateComposite
- Description: 추가할 때 지정한 이름으로 Composite를 찾아 갱신한다.
- Declaration: `Source/NXPlanet/NXOverlay.h:148`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:232`

## UpdateSource
- Description: 오버레이 레이어의 내용을 갱신하도록 한다.
- Declaration: `Source/NXPlanet/NXOverlay.h:157`
- Implementation: `Source/NXPlanet/NXOverlay.cpp:217`
