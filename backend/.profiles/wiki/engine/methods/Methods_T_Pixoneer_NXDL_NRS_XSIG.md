---
title: Pixoneer.NXDL.NRS.XSIG Methods
aliases:
  - XSIG Methods
  - Pixoneer.NXDL.NRS.XSIG
  - XSIG
symbols:
  - XSIG
  - AddROI
  - CalcStatistics
  - GetCorrelation
  - GetCovariance
  - GetCovarianceDeterminant
  - GetCovarianceInverse
  - GetHistogram
  - GetMax
  - GetMean
  - GetMin
  - GetROIAt
  - GetROISize
  - GetStd
  - RemoveROIAll
  - RemoveROIAt
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
- Type: `XSIG`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XSIG.htm`
- Type declaration: `Source/NXDLrs/NXDLrs.h:362`
- Method count: `15`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XSIG
type_name: XSIG
namespace: Pixoneer.NXDL.NRS
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
## AddROI
- Description: Signature를 이루는 ROI를 추가한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:378`
- Implementation: `Source/NXDLrs/XSIG.cpp:41`

## CalcStatistics
- Description: 입력된 밴드의 SIG 영역에 대해서 통계값을 계산한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:401`
- Implementation: `Source/NXDLrs/XSIG.cpp:120`

## GetCorrelation
- Description: Band Index의 두 밴드 데이터에 대한 Signature 상관도값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:443`
- Implementation: `Source/NXDLrs/XSIG.cpp:191`

## GetCovariance
- Description: Band Index의 두 밴드 데이터에 대한 Signature 공분산값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:427`
- Implementation: `Source/NXDLrs/XSIG.cpp:173`

## GetCovarianceDeterminant
- Description: Signature의 공분산 Determinant값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:437`
- Implementation: `Source/NXDLrs/XSIG.cpp:185`

## GetCovarianceInverse
- Description: Band Index의 두 밴드 데이터에 대한 Signature 공분산 역수값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:433`
- Implementation: `Source/NXDLrs/XSIG.cpp:179`

## GetHistogram
- Description: Band Index의 밴드 데이터에 대한 Signature 히스토그램 값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:449`
- Implementation: `Source/NXDLrs/XSIG.cpp:197`

## GetMax
- Description: Band Index의 밴드 데이터에 대한 Signature 최댓값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:411`
- Implementation: `Source/NXDLrs/XSIG.cpp:155`

## GetMean
- Description: Band Index의 밴드 데이터에 대한 Signature 평균값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:416`
- Implementation: `Source/NXDLrs/XSIG.cpp:161`

## GetMin
- Description: Band Index의 밴드 데이터에 대한 Signature 최솟값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:406`
- Implementation: `Source/NXDLrs/XSIG.cpp:149`

## GetROIAt
- Description: Signature를 생성하기 위해 추가된 ROI 중 해당 Index에 대한 ROI를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:383`
- Implementation: `Source/NXDLrs/XSIG.cpp:47`

## GetROISize
- Description: Signature를 생성하기 위한 총 ROI의 수를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:387`
- Implementation: `Source/NXDLrs/XSIG.cpp:56`

## GetStd
- Description: Band Index의 밴드 데이터에 대한 Signature 표준편차값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:421`
- Implementation: `Source/NXDLrs/XSIG.cpp:167`

## RemoveROIAll
- Description: 모든 ROI를 삭제한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:394`
- Implementation: `Source/NXDLrs/XSIG.cpp:69`

## RemoveROIAt
- Description: Signature를 생성하기 위해 추가된 ROI 중 해당 Index에 대한 ROI를 지운다.
- Declaration: `Source/NXDLrs/NXDLrs.h:391`
- Implementation: `Source/NXDLrs/XSIG.cpp:62`
