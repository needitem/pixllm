---
title: Pixoneer.NXDL.NRSEX.XDMBandFeatureExt Methods
aliases:
  - XDMBandFeatureExt Methods
  - Pixoneer.NXDL.NRSEX.XDMBandFeatureExt
  - XDMBandFeatureExt
symbols:
  - XDMBandFeatureExt
  - CreateFeature
  - DilateFeature
  - ErodeFeature
  - ExpandFeature
  - ExtractFeatureFromSeedPixel
  - ExtractFeatureFromSeedPolygon
  - GetInputParam
  - GetPolygon
  - SetInputParam
  - ShrinkFeature
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
- Type: `XDMBandFeatureExt`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRSEX_XDMBandFeatureExt.htm`
- Type declaration: `Source/NXDLrsEx/XDMBandFeatureExt.h:149`
- Method count: `10`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRSEX.XDMBandFeatureExt
type_name: XDMBandFeatureExt
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
## CreateFeature
- Description: 새 feature 를 생성하여 추가한다.
- Declaration: `Source/NXDLrsEx/XDMBandFeatureExt.h:173`
- Implementation: `Source/NXDLrsEx/XDMBandFeatureExt.cpp:112`

## DilateFeature
- Description: Feature 영역을 넓힌다.
- Declaration: `Source/NXDLrsEx/XDMBandFeatureExt.h:196`
- Implementation: `Source/NXDLrsEx/XDMBandFeatureExt.cpp:184`

## ErodeFeature
- Description: Feature 영역을 erode 한다.
- Declaration: `Source/NXDLrsEx/XDMBandFeatureExt.h:202`
- Implementation: `Source/NXDLrsEx/XDMBandFeatureExt.cpp:197`

## ExpandFeature
- Description: Feature 영역을 확장 한다.
- Declaration: `Source/NXDLrsEx/XDMBandFeatureExt.h:208`
- Implementation: `Source/NXDLrsEx/XDMBandFeatureExt.cpp:210`

## ExtractFeatureFromSeedPixel
- Description: 입력한 한 픽셀의 특성을 이용해서 feature 를 추출한다 .
- Declaration: `Source/NXDLrsEx/XDMBandFeatureExt.h:181`
- Implementation: `Source/NXDLrsEx/XDMBandFeatureExt.cpp:139`

## ExtractFeatureFromSeedPolygon
- Description: 입력한 특정 영역의 특성을 이용해서 feature 를 추출한다 .
- Declaration: `Source/NXDLrsEx/XDMBandFeatureExt.h:190`
- Implementation: `Source/NXDLrsEx/XDMBandFeatureExt.cpp:152`

## GetInputParam
- Description: 화소 추출을 위한 입력 파라미터를 얻는다.
- Declaration: `Source/NXDLrsEx/XDMBandFeatureExt.h:167`
- Implementation: `Source/NXDLrsEx/XDMBandFeatureExt.cpp:107`

## GetPolygon
- Description: Feature 영역 내 화소값 한 개당 XvcPolygon 으로 생성해서 arrPolygon 에 추가한다.
- Declaration: `Source/NXDLrsEx/XDMBandFeatureExt.h:218`
- Implementation: `Source/NXDLrsEx/XDMBandFeatureExt.cpp:121`

## SetInputParam
- Description: 화소 추출을 위한 입력 파라미터를 설정.
- Declaration: `Source/NXDLrsEx/XDMBandFeatureExt.h:163`
- Implementation: `Source/NXDLrsEx/XDMBandFeatureExt.cpp:73`

## ShrinkFeature
- Description: Feature 영역을 줄인다.
- Declaration: `Source/NXDLrsEx/XDMBandFeatureExt.h:214`
- Implementation: `Source/NXDLrsEx/XDMBandFeatureExt.cpp:223`
