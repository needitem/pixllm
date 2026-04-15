---
title: Pixoneer.NXDL.NRSEX.XMosaicHelper Methods
aliases:
  - XMosaicHelper Methods
  - Pixoneer.NXDL.NRSEX.XMosaicHelper
  - XMosaicHelper
symbols:
  - XMosaicHelper
  - AddXRSFile
  - ApplyMask
  - CreateSeamlineStart
  - DoRunHistogramMatching
  - GetBand
  - GetDisplayBand
  - GetIntersectInfo
  - GetNumOfBand
  - GetNumOfMosaicManager
  - SetHistogramType
  - SetIntersectInfo
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nrsex
---

# Overview
- Namespace: `Pixoneer.NXDL.NRSEX`
- Type: `XMosaicHelper`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRSEX_XMosaicHelper.htm`
- Type declaration: `Source/NXDLrsEx/XMosaicHelper.h:24`
- Method count: `11`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRSEX.XMosaicHelper
type_name: XMosaicHelper
namespace: Pixoneer.NXDL.NRSEX
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
## AddXRSFile
- Description: 모자이크를 수행하기 위한 영상을 추가한다.
- Declaration: `Source/NXDLrsEx/XMosaicHelper.h:46`
- Implementation: `Source/NXDLrsEx/XMosaicHelper.cpp:49`, `Source/NXDLrsEx/XMosaicHelper.cpp:68`

## ApplyMask
- Description: 2장 영상에 대한 접합선을 이용하여 마스크를 적용한다.
- Declaration: `Source/NXDLrsEx/XMosaicHelper.h:80`
- Implementation: `Source/NXDLrsEx/XMosaicHelper.cpp:136`

## CreateSeamlineStart
- Description: 모자이크를 위한 접합선 생성을 수행한다.
- Declaration: `Source/NXDLrsEx/XMosaicHelper.h:55`
- Implementation: `Source/NXDLrsEx/XMosaicHelper.cpp:80`

## DoRunHistogramMatching
- Description: 2장 영상 모자이크 수행시 히스토그램 매칭을 수행한다.
- Declaration: `Source/NXDLrsEx/XMosaicHelper.h:91`
- Implementation: `Source/NXDLrsEx/XMosaicHelper.cpp:150`

## GetBand
- Description: 2장씩 모자이크된 결과 영상의 각 밴드를 가져온다.
- Declaration: `Source/NXDLrsEx/XMosaicHelper.h:70`
- Implementation: `Source/NXDLrsEx/XMosaicHelper.cpp:116`

## GetDisplayBand
- Description: 2장씩 모자이크된 결과 영상의 display 용 XDMBandMosaicLT 객체를 가져온다.
- Declaration: `Source/NXDLrsEx/XMosaicHelper.h:64`
- Implementation: `Source/NXDLrsEx/XMosaicHelper.cpp:103`

## GetIntersectInfo
- Description: 2장 영상에 대한 접합선 정보를 가져온다.
- Declaration: `Source/NXDLrsEx/XMosaicHelper.h:99`
- Implementation: `Source/NXDLrsEx/XMosaicHelper.cpp:158`

## GetNumOfBand
- Description: 2장씩 모자이크된 결과 영상의 밴드 개수를 가져온다.
- Declaration: `Source/NXDLrsEx/XMosaicHelper.h:75`
- Implementation: `Source/NXDLrsEx/XMosaicHelper.cpp:129`

## GetNumOfMosaicManager
- Description: 영상 2 장씩 모자이크 처리하기 위한 기능을 정의한 내부 클래스인 MosaicManager 개수를 가져온다.
- Declaration: `Source/NXDLrsEx/XMosaicHelper.h:59`
- Implementation: `Source/NXDLrsEx/XMosaicHelper.cpp:96`

## SetHistogramType
- Description: 2장 영상 모자이크 수행시 적용하기 위한 histogram 매칭방식을 설정한다.
- Declaration: `Source/NXDLrsEx/XMosaicHelper.h:86`
- Implementation: `Source/NXDLrsEx/XMosaicHelper.cpp:143`

## SetIntersectInfo
- Description: 2장 영상의 접합선 정보를 설정한다.
- Declaration: `Source/NXDLrsEx/XMosaicHelper.h:105`
- Implementation: `Source/NXDLrsEx/XMosaicHelper.cpp:186`
