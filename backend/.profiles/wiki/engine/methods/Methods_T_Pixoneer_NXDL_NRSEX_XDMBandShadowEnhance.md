---
title: Pixoneer.NXDL.NRSEX.XDMBandShadowEnhance Methods
aliases:
  - XDMBandShadowEnhance Methods
  - Pixoneer.NXDL.NRSEX.XDMBandShadowEnhance
  - XDMBandShadowEnhance
symbols:
  - XDMBandShadowEnhance
  - AddRegion
  - GetInputParam
  - GetNumRegions
  - RemoveRegionAt
  - SetInputParam
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
- Type: `XDMBandShadowEnhance`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRSEX_XDMBandShadowEnhance.htm`
- Type declaration: `Source/NXDLrsEx/XDMBandShadowEnhance.h:176`
- Method count: `5`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRSEX.XDMBandShadowEnhance
type_name: XDMBandShadowEnhance
namespace: Pixoneer.NXDL.NRSEX
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
## AddRegion
- Description: 그림자 개선을 수행하기 위한 영역 설정. 영역 내 한 픽셀당 XvcPolygon 한개를 생성해서 Array 에 추가한다. XDMBandFeatureExt::SetPolygon([OutAttribute] ArrayList^% arrPolygon) 과 연계하여 사용 가능.
- Declaration: `Source/NXDLrsEx/XDMBandShadowEnhance.h:202`, `Source/NXDLrsEx/XDMBandShadowEnhance.h:207`
- Implementation: `Source/NXDLrsEx/XDMBandShadowEnhance.cpp:69`, `Source/NXDLrsEx/XDMBandShadowEnhance.cpp:90`

## GetInputParam
- Description: 그림자 개선을 위한 입력 파라미터를 얻는다.
- Declaration: `Source/NXDLrsEx/XDMBandShadowEnhance.h:194`
- Implementation: `Source/NXDLrsEx/XDMBandShadowEnhance.cpp:64`

## GetNumRegions
- Description: 추가된 그림자 개선 영역 개수를 가져온다.
- Declaration: `Source/NXDLrsEx/XDMBandShadowEnhance.h:215`
- Implementation: `Source/NXDLrsEx/XDMBandShadowEnhance.cpp:106`

## RemoveRegionAt
- Description: 해당 index 의 그림자 개선 영역 삭제.
- Declaration: `Source/NXDLrsEx/XDMBandShadowEnhance.h:211`
- Implementation: `Source/NXDLrsEx/XDMBandShadowEnhance.cpp:100`

## SetInputParam
- Description: 그림자 개선을 위한 입력 파라미터를 설정.
- Declaration: `Source/NXDLrsEx/XDMBandShadowEnhance.h:190`
- Implementation: `Source/NXDLrsEx/XDMBandShadowEnhance.cpp:52`
