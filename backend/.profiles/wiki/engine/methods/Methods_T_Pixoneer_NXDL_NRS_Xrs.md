---
title: Pixoneer.NXDL.NRS.Xrs Methods
aliases:
  - Xrs Methods
  - Pixoneer.NXDL.NRS.Xrs
  - Xrs
symbols:
  - Xrs
  - CalcGaussianRange95
  - CalcGaussianRange98
  - CalcNCC
  - CalcStretchedHistogramByCut
  - GeoTransformToWarpCoeff
  - SplineInterpolate
  - StretchLUT
  - WarpCoeffToGeoTransform
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
- Type: `Xrs`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_Xrs.htm`
- Type declaration: `Source/NXDLrs/NXDLrs.h:2210`
- Method count: `8`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.Xrs
type_name: Xrs
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
## CalcGaussianRange95
- Description: 히스토그램에 대한 통계분포를 계산하여 Gaussian 95%에 해당하는 범위에 해당하는 최소/최댓값을 계산한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2289`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:127`

## CalcGaussianRange98
- Description: 히스토그램에 대한 통계분포를 계산하여 Gaussian 98%에 해당하는 범위에 해당하는 최소/최댓값을 계산한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2321`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:143`

## CalcNCC
- Description: Normalized Cross Correlation를 계산한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2336`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:159`

## CalcStretchedHistogramByCut
- Description: 인덱스에 대응하는 색합성 밴드에 대비 신장 최소/최댓값을 적용한 결과 히스토그램을 생성한다. 색합성의 StretchCoverage 값에 따른 데이터 통계치를 이용해 히스토그램을 생성한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2236`, `Source/NXDLrs/NXDLrs.h:2247`, `Source/NXDLrs/NXDLrs.h:2257`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:80`, `Source/NXDLrs/NXDLrs.cpp:85`, `Source/NXDLrs/NXDLrs.cpp:106`

## GeoTransformToWarpCoeff
- Description: GeoTransform 정보를 XWarpCoeff의 변환 계수 순서로 변경한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2354`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:211`

## SplineInterpolate
- Description: Spline 보간을 수행한다. 두 개의 입력 데이터 배열 크기는 같아야 한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2344`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:170`

## StretchLUT
- Description: 영상 향상을 위한 LUT(Look Up Table)와 신장된 히스토그램을 생성한다. 히스토그램 신장(Histogram Stretching)에 대해서는 영상처리 전문서적을 참고한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2225`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:24`

## WarpCoeffToGeoTransform
- Description: XWarpCoeff의 변환 계수를 GeoTransform 정보 순서로 변경한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2364`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:230`
