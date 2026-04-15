---
title: Pixoneer.NXDL.NRS.XDMBandImageSharpen Methods
aliases:
  - XDMBandImageSharpen Methods
  - Pixoneer.NXDL.NRS.XDMBandImageSharpen
  - XDMBandImageSharpen
symbols:
  - XDMBandImageSharpen
  - DoPCASharpenPreProcess
  - GetBandB
  - GetBandG
  - GetBandR
  - GetInputParam
  - SetInputParam
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nrs
---

# Overview
- Namespace: `Pixoneer.NXDL.NRS`
- Type: `XDMBandImageSharpen`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XDMBandImageSharpen.htm`
- Type declaration: `Source/NXDLrs/XDMBandImageSharpen.h:171`
- Method count: `6`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XDMBandImageSharpen
type_name: XDMBandImageSharpen
namespace: Pixoneer.NXDL.NRS
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
## DoPCASharpenPreProcess
- Description: 제1주성분의 최소/최대 화소값과 PCA 성분을 역변환한 데이터 각각의 최소/최대 화소값을 미리 계산한다.
- Declaration: `Source/NXDLrs/XDMBandImageSharpen.h:210`
- Implementation: `Source/NXDLrs/XDMBandImageSharpen.cpp:197`

## GetBandB
- Description: 생성된 고해상도 Color 영상 중 Blue 영상밴드를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandImageSharpen.h:205`
- Implementation: `Source/NXDLrs/XDMBandImageSharpen.cpp:182`

## GetBandG
- Description: 생성된 고해상도 Color 영상 중 Green 영상밴드를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandImageSharpen.h:203`
- Implementation: `Source/NXDLrs/XDMBandImageSharpen.cpp:167`

## GetBandR
- Description: 생성된 고해상도 Color 영상 중 Red 영상밴드를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandImageSharpen.h:201`
- Implementation: `Source/NXDLrs/XDMBandImageSharpen.cpp:152`

## GetInputParam
- Description: 입력파라미터를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandImageSharpen.h:198`
- Implementation: `Source/NXDLrs/XDMBandImageSharpen.cpp:146`

## SetInputParam
- Description: Image sharpening 영상처리를 위한 입력 파라미터를 설정한다.
- Declaration: `Source/NXDLrs/XDMBandImageSharpen.h:194`
- Implementation: `Source/NXDLrs/XDMBandImageSharpen.cpp:115`
