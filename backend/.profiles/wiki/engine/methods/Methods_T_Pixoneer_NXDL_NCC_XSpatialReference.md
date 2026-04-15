---
title: Pixoneer.NXDL.NCC.XSpatialReference Methods
aliases:
  - XSpatialReference Methods
  - Pixoneer.NXDL.NCC.XSpatialReference
  - XSpatialReference
symbols:
  - XSpatialReference
  - Clone
  - exportToPrettyWkt
  - exportToProj4
  - exportToWkt
  - FindBestEPSGMatch
  - GetAreaOfUse
  - GetUTMZone
  - importFromEPSG
  - importFromESRI
  - importFromProj4
  - importFromWkt
  - IsGeocentric
  - IsGeographic
  - IsLocal
  - IsProjected
  - IsSame
  - IsUTM
  - SetUTM
  - SetWellKnownGeogCS
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - ncc
---

# Overview
- Namespace: `Pixoneer.NXDL.NCC`
- Type: `XSpatialReference`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NCC_XSpatialReference.htm`
- Type declaration: `Source/NXDLcc/NXDLcc.h:91`
- Method count: `19`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NCC.XSpatialReference
type_name: XSpatialReference
namespace: Pixoneer.NXDL.NCC
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
## Clone
- Description: 이 객체와 동일한 XSpatialReference객체를 생성하여 반환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:202`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:245`

## exportToPrettyWkt
- Description: XSpartialReference객체를 구성하는 파라미터를 가독성이 높게 Well Known Text(WKT)형태로 변환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:123`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:116`

## exportToProj4
- Description: XSpartialReference객체를 구성하는 파라미터를 Proj.4형태로 변환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:128`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:125`

## exportToWkt
- Description: XSpartialReference객체를 구성하는 파라미터를 Well Known Text(WKT)형태로 변환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:118`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:107`

## FindBestEPSGMatch
- Description: EPSG 코드에서 최적의 좌표체계를 찾아 EPSG 문자열을 반환한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:219`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:274`

## GetAreaOfUse
- Description: 좌표체계의 유효 사용영역을 확인한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:213`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:251`

## GetUTMZone
- Description: 객체의 UTM Zone에 대한 정보를 획득한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:194`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:232`

## importFromEPSG
- Description: 입력 EPSG 코드값으로 좌표계를 초기화한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:133`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:149`

## importFromESRI
- Description: ESRI 상용 제품의 고유 포맷인 .prj파일을 이용하여 좌표계를 초기화한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:143`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:171`

## importFromProj4
- Description: proj4 형식의 문자열값을 이용하여 좌표계를 초기화한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:148`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:183`

## importFromWkt
- Description: WKT 형식의 문자열을 이용하여 좌표계를 초기화한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:138`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:159`

## IsGeocentric
- Description: Geocentric 좌표 시스템(ECEF)인지 여부를 확인한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:160`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:205`

## IsGeographic
- Description: Geographic 좌표 시스템인지 여부를 확인한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:152`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:195`

## IsLocal
- Description: Local좌표 시스템인지 여부를 확인한다. 좌표계는 통상 이용되는 범위에 따라 전지구적 차원에서사용되는 Global좌표계와 일부 지역(Local)에서만 사용하는 지역적 좌표계로 분류한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:165`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:210`

## IsProjected
- Description: 투영 좌표 시스템인지 여부를 확인한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:156`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:200`

## IsSame
- Description: 좌표계 시스템이 동일한지 확인한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:170`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:215`

## IsUTM
- Description: UTM 좌표 시스템인지를 확인한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:198`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:240`

## SetUTM
- Description: 입력 Zone 및 북반구 정보를 이용하여 UTM 좌표계를 설정한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:189`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:220`

## SetWellKnownGeogCS
- Description: 자주 사용하는 좌표계를 문자열로 정의하여 좌표계를 초기화한다. "WGS84" : "EPSG:4326" 와 동일 "WGS72" : "EPSG:4322" 와 동일 "NAD27" : "EPSG:4267" 와 동일 "NAD83" : "EPSG:4269" 와 동일 "EPSG:n" : ImportFromEPSG(n) 와 동일한 기능을 하는 Well Known Text.
- Declaration: `Source/NXDLcc/NXDLcc.h:183`
- Implementation: `Source/NXDLcc/XSpatialReference.cpp:142`
