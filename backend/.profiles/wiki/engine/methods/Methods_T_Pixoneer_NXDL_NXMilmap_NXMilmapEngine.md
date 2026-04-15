---
title: Pixoneer.NXDL.NXMilmap.NXMilmapEngine Methods
aliases:
  - NXMilmapEngine Methods
  - Pixoneer.NXDL.NXMilmap.NXMilmapEngine
  - NXMilmapEngine
symbols:
  - NXMilmapEngine
  - AddView
  - DestoryView
  - FindScale
  - GetNumOfPBPScale
  - GetNumOfScale
  - GetPBPScaleID
  - GetPBPScaleName
  - GetScaleID
  - GetScaleName
  - GetScalePixelSize
  - InitFromXML
  - IsPBPScaleUsable
  - IsScaleUsable
  - PreTranslateMessage
  - SetDefaultScales
  - SetDefaultScalesPBP
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
- Type: `NXMilmapEngine`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXMilmap_NXMilmapEngine.htm`
- Type declaration: `Source/NXMilmap/NXMilmapEngine.h:23`
- Method count: `16`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXMilmap.NXMilmapEngine
type_name: NXMilmapEngine
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
## AddView
- Description: 엔진에 NXMilmapView를 추가한다. 이 함수는 윈도우 컨트롤이 호출한다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:37`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:96`

## DestoryView
- Description: 엔진에서 NXMilmapView를 소멸시킨다. 이 함수는 윈도우 컨트롤이 호출한다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:42`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:125`

## FindScale
- Description: 입력 ID와 일치하는 축척을 검색하여 반환한다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:72`, `Source/NXMilmap/NXMilmapEngine.h:77`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:244`, `Source/NXMilmap/NXMilmapEngine.cpp:250`

## GetNumOfPBPScale
- Description: 엔진에서 사용하고 있는 지명 축척의 개수를 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:95`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:265`

## GetNumOfScale
- Description: 엔진에서 사용하고 있는 축척의 개수를 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:91`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:259`

## GetPBPScaleID
- Description: 입력 인덱스에 대응하는 지명 축척의 ID를 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:115`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:306`

## GetPBPScaleName
- Description: 입력 인덱스에 대응하는 지명 축척의 이름을 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:105`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:296`

## GetScaleID
- Description: 입력 인덱스에 대응하는 축척의 ID를 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:110`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:277`

## GetScaleName
- Description: 입력 인덱스에 대응하는 축척의 이름을 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:100`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:271`

## GetScalePixelSize
- Description: 입력 인덱스에 대응하는 축척의 해상도를 가져온다. 단위는 degree.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:121`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:285`

## InitFromXML
- Description: 환경설정 파일을 읽어 초기화한다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:32`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:73`

## IsPBPScaleUsable
- Description: 입력 지명 축척 인덱스가 유효한지를 확인한다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:57`, `Source/NXMilmap/NXMilmapEngine.h:67`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:230`, `Source/NXMilmap/NXMilmapEngine.cpp:236`

## IsScaleUsable
- Description: 입력 축척 인덱스가 유효한지를 확인한다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:52`, `Source/NXMilmap/NXMilmapEngine.h:62`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:216`, `Source/NXMilmap/NXMilmapEngine.cpp:222`

## PreTranslateMessage
- Description: 윈도우 메시지를 보내기 전에 맵 엔진에서 메시지를 처리하기 위해 사용된다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:47`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:142`

## SetDefaultScales
- Description: 새로운 축척 데이터로 지도를 설정한다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:126`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:343`

## SetDefaultScalesPBP
- Description: 새로운 축척 데이터로 지도를 설정한다.
- Declaration: `Source/NXMilmap/NXMilmapEngine.h:131`
- Implementation: `Source/NXMilmap/NXMilmapEngine.cpp:353`
