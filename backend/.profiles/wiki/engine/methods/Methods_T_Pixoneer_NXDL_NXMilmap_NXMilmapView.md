---
title: Pixoneer.NXDL.NXMilmap.NXMilmapView Methods
aliases:
  - NXMilmapView Methods
  - Pixoneer.NXDL.NXMilmap.NXMilmapView
  - NXMilmapView
symbols:
  - NXMilmapView
  - AddRenderLayer
  - CalculateCADRGScale
  - CalculateScale
  - CaptureScreen
  - CheckMilmapData
  - GetDrawArgs
  - GetHandle
  - GetNativePtr
  - IsExistScale
  - IsUnderMouse
  - RefreshScreen
  - RemoveRenderLayer
  - SearchName
  - SearchScale
  - SetGeoToCenter
  - SetResolutionThreshold
  - SetViewZoomCenterPosition
  - ShowCross
  - Zoom
  - ZoomFitRect
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nxmilmap
---

# Overview
- Namespace: `Pixoneer.NXDL.NXMilmap`
- Type: `NXMilmapView`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXMilmap_NXMilmapView.htm`
- Type declaration: `Source/NXMilmap/NXMilmapView.h:65`
- Method count: `20`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXMilmap.NXMilmapView
type_name: NXMilmapView
namespace: Pixoneer.NXDL.NXMilmap
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
## AddRenderLayer
- Description: 렌더 레이어를 추가한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:165`, `Source/NXMilmap/NXMilmapView.h:220`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:365`, `Source/NXMilmap/NXMilmapView.cpp:366`, `Source/NXMilmap/NXMilmapView.cpp:372`, `Source/NXMilmap/NXMilmapView.cpp:373`

## CalculateCADRGScale
- Description: CADRG 축척에 따른 비율을 계산한다. CADRG NS PixelSize과의 비율을 이용하여 축척을 계산하여 반환한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:250`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:596`

## CalculateScale
- Description: 현재 뷰를 기준으로 축척을 계산한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:246`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:590`

## CaptureScreen
- Description: 화면을 캡쳐한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:120`, `Source/NXMilmap/NXMilmapView.h:426`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:734`, `Source/NXMilmap/NXMilmapView.cpp:742`

## CheckMilmapData
- Description: 특정 위경도 위치에 대해 Milmap 데이터가 있는지 확인한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:110`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:301`

## GetDrawArgs
- Description: 이 뷰의 도시 인수를 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:242`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:460`

## GetHandle
- Description: 뷰 컨트롤 핸들을 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:100`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:81`

## GetNativePtr
- Description: NXMilmapView 원본 비관리 객체 포인터를 가져온다. c# 사용 불가.
- Declaration: `Source/NXMilmap/NXMilmapView.h:104`
- Implementation: `not found`

## IsExistScale
- Description: 입력 인덱스에 맞는 축척이 있는지 확인한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:146`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:345`

## IsUnderMouse
- Description: 마우스가 뷰 위에 있는지를 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:487`
- Implementation: `not found`

## RefreshScreen
- Description: 화면을 갱신한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:159`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:358`

## RemoveRenderLayer
- Description: 뷰에 레이어를 분리한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:170`, `Source/NXMilmap/NXMilmapView.h:225`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:393`, `Source/NXMilmap/NXMilmapView.cpp:394`, `Source/NXMilmap/NXMilmapView.cpp:409`, `Source/NXMilmap/NXMilmapView.cpp:410`

## SearchName
- Description: 인덱스에 맞는 축척의 이름을 검색한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:151`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:320`

## SearchScale
- Description: 축척을 검색한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:125`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:311`

## SetGeoToCenter
- Description: 특정 축척에 대한 입력 중심점으로 이동한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:116`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:292`

## SetResolutionThreshold
- Description: 뷰의 렌더링 해상도 범위를 제한한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:255`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:781`

## SetViewZoomCenterPosition
- Description: 해당 좌표를 기준으로 마우스 휠 줌을 한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:259`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:789`

## ShowCross
- Description: 십자 UI 도시를 보일지 여부를 설정한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:155`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:352`

## Zoom
- Description: 줌 인수에 따라 확대축소한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:131`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:328`

## ZoomFitRect
- Description: 화면 영역을 명시하고 영역에 맞게 화면을 확대축소한다.
- Declaration: `Source/NXMilmap/NXMilmapView.h:141`
- Implementation: `Source/NXMilmap/NXMilmapView.cpp:334`
