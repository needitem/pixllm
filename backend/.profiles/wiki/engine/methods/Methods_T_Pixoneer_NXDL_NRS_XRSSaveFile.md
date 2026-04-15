---
title: Pixoneer.NXDL.NRS.XRSSaveFile Methods
aliases:
  - XRSSaveFile Methods
  - Pixoneer.NXDL.NRS.XRSSaveFile
  - XRSSaveFile
symbols:
  - XRSSaveFile
  - AddBand
  - AddGCPSet
  - GetBandAt
  - GetBoundRect
  - GetNativePtr
  - SetGeoTransform
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
- Type: `XRSSaveFile`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XRSSaveFile.htm`
- Type declaration: `Source/NXDLrs/XRSFile.h:1164`
- Method count: `6`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XRSSaveFile
type_name: XRSSaveFile
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
## AddBand
- Description: Band를 추가한다.
- Declaration: `Source/NXDLrs/XRSFile.h:1184`
- Implementation: `Source/NXDLrs/XRSFile.cpp:471`

## AddGCPSet
- Description: GCP Set을 추가한다.
- Declaration: `Source/NXDLrs/XRSFile.h:1199`
- Implementation: `Source/NXDLrs/XRSFile.cpp:477`

## GetBandAt
- Description: 입력 인덱스에 해당하는 Band를 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:1189`, `Source/NXDLrs/XRSFile.h:1195`
- Implementation: `Source/NXDLrs/XRSFile.cpp:516`, `Source/NXDLrs/XRSFile.cpp:525`

## GetBoundRect
- Description: 설정된 Bounary값을 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:1206`
- Implementation: `Source/NXDLrs/XRSFile.cpp:552`

## GetNativePtr
- Description: XRSSaveFile의 원본 비관리 객체 포인터를 반환한다. C#에서 사용 불가.
- Declaration: `Source/NXDLrs/XRSFile.h:1180`
- Implementation: `not found`

## SetGeoTransform
- Description: GeoTransform 을 수행하기 위한 Affine Transform 계수와 좌표계 정보를 설정한다.
- Declaration: `Source/NXDLrs/XRSFile.h:1215`
- Implementation: `Source/NXDLrs/XRSFile.cpp:637`
