---
title: Pixoneer.NXDL.NRS.XRSLoadFile Methods
aliases:
  - XRSLoadFile Methods
  - Pixoneer.NXDL.NRS.XRSLoadFile
  - XRSLoadFile
symbols:
  - XRSLoadFile
  - CalcStatistics
  - GetBandAt
  - GetBoundRect
  - GetCorrelationMatrix
  - GetCovarianceMatrix
  - GetGCPSetsAt
  - GetGeographicBound
  - GetGeoTransform
  - GetNativePtr
  - IsValidGeoTransform
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
- Type: `XRSLoadFile`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XRSLoadFile.htm`
- Type declaration: `Source/NXDLrs/XRSFile.h:962`
- Method count: `10`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XRSLoadFile
type_name: XRSLoadFile
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
## CalcStatistics
- Description: 로딩된 Band들에 대한 통계값을 강제로 재계산한다.
- Declaration: `Source/NXDLrs/XRSFile.h:1013`
- Implementation: `Source/NXDLrs/XRSFile.cpp:224`

## GetBandAt
- Description: 입력 인덱스에 대한 Band를 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:986`
- Implementation: `Source/NXDLrs/XRSFile.cpp:125`

## GetBoundRect
- Description: 로딩된 파일의 Boundary값을 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:998`
- Implementation: `Source/NXDLrs/XRSFile.cpp:161`

## GetCorrelationMatrix
- Description: 각 영상 밴드간의 Correlation matrix를 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:1008`
- Implementation: `Source/NXDLrs/XRSFile.cpp:205`

## GetCovarianceMatrix
- Description: 각 영상 밴드간의 Covariance matrix를 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:1003`
- Implementation: `Source/NXDLrs/XRSFile.cpp:186`

## GetGCPSetsAt
- Description: 입력 인덱스에 대한 GCP set을 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:991`
- Implementation: `Source/NXDLrs/XRSFile.cpp:135`

## GetGeographicBound
- Description: 로딩된 영상에 대하여 실제 적용된 좌표 시스템과 상관없이 위경도 좌표계로 영상의 4개 모서리 값을 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:1021`, `Source/NXDLrs/XRSFile.h:1025`
- Implementation: `Source/NXDLrs/XRSFile.cpp:294`, `Source/NXDLrs/XRSFile.cpp:330`

## GetGeoTransform
- Description: GeoTransform을 수행하기 위한 Affine Transform 계수와 좌표계 정보를 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:1080`
- Implementation: `Source/NXDLrs/XRSFile.cpp:391`

## GetNativePtr
- Description: XRSLoadFile의 원본 비관리 객체 포인터를 반환한다. C#에서 사용 불가.
- Declaration: `Source/NXDLrs/XRSFile.h:981`
- Implementation: `not found`

## IsValidGeoTransform
- Description: GeoTransform 정보가 유효한지 여부를 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:1086`
- Implementation: `Source/NXDLrs/XRSFile.cpp:410`
