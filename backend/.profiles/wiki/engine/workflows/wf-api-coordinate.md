---
title: Coordinate API Workflow
description: Convert coordinate codes, define spatial references, and transform points between coordinate systems.
aliases:
  - coordinate api
  - coordinate transform
  - lat lon utm
  - mgrs georef
  - spatial reference usage
  - xcc usage
  - 좌표계 변환 사용법
  - lat lon 좌표계를 utm 좌표계로 변경
  - epsg 코드로 좌표계 생성
  - 좌표계가 utm인지 확인
  - utm zone 확인
  - lat lon 좌표를 mgrs로 변환
  - georef 좌표를 lat lon으로 변환
  - 좌표 한 점 변환하는 방법
  - 두 좌표계 사이 좌표 변환
  - 좌표변환 사용법
symbols:
  - Xcc
  - XCoordinateTransformation
  - XSpatialReference
tags:
  - engine
  - workflow
  - api
  - coordinate
---

# Overview
- Goal: answer most coordinate-system questions from one page.
- This workflow covers `Xcc` code conversion, `XCoordinateTransformation`, and `XSpatialReference`.
- For the current wiki routing, use this family for SR/code conversion and explicit coordinate-system transforms, not for sensor-model projection or image-center map-coordinate questions.
- For the current wiki routing, generic `좌표변환`, `좌표 한 점 변환`, or `두 좌표계 사이 변환` without image/ground projection words are handled here.

## Primary Usage Buckets
- `좌표 코드 변환`: `WGP2UTM`, `UTM2WGP`, `WGP2MGRS`, `MGRS2WGP`, `WGP2GEOREF`, `GEOREF2WGP`
- `좌표 한 점 변환`: `CreateCoordinateTransform`, `TransformPt`
- `좌표계 생성/내보내기`: `ImportFromEPSG`, `ImportFromWkt`, `ImportFromProj4`, `ExportToWkt`, `ExportToPrettyWkt`, `ExportToProj4`
- `좌표계 판별`: `IsGeographic`, `IsProjected`, `IsUTM`, `GetUTMZone`, `GetAreaOfUse`, `IsSame`

## Related Sources
- [NXDLcc source](../pages/sources/nxdlcc.md)

## Practical Answer Shape
- `좌표 코드 변환`: `WGP/UTM/MGRS/GEOREF` 계열 변환 함수를 먼저 제시합니다.
- `좌표 한 점 변환`: `CreateCoordinateTransform` 후 `TransformPt` 순서로 설명합니다.
- `좌표계 생성/출력`: `ImportFromEPSG/Wkt/Proj4`와 `ExportTo*`를 짝으로 설명합니다.
- `좌표계 판별`: `IsGeographic/Projected/UTM`, `GetUTMZone` 같은 판별 메서드로 답합니다.


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

## Knowledge Bundle
```yaml
concept_terms:
- spatial reference
- coordinate transform
- utm
- wgs84
bundle_pages:
- path: pages/howtos/coordinate-conversion-recipes.md
  relation: family_howto
- path: pages/concepts/spatial-reference-and-coordinate-transform.md
  relation: family_concept
- path: workflows/wf-api-sensor-model.md
  relation: dependency_workflow
- path: pages/sources/nxdlcc.md
  relation: source_summary
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-20T02:38:44Z`.
- Resolved required symbols: `17/17`
- Linked modules:
  - `NXDLcc`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
```yaml
workflow_family: api_coordinate
output_shape: focused_snippet_or_helper
required_symbols:
  - Xcc.WGP2UTM
  - Xcc.UTM2WGP
  - Xcc.WGP2MGRS
  - Xcc.MGRS2UTM
  - Xcc.MGRS2WGP
  - Xcc.WGP2GEOREF
  - Xcc.GEOREF2WGP
  - XCoordinateTransformation.CreateCoordinateTransform
  - XCoordinateTransformation.TransformPt
  - XSpatialReference.ImportFromEPSG
  - XSpatialReference.ImportFromWkt
  - XSpatialReference.ImportFromProj4
  - XSpatialReference.ExportToWkt
  - XSpatialReference.ExportToPrettyWkt
  - XSpatialReference.ExportToProj4
  - XSpatialReference.GetUTMZone
  - XSpatialReference.IsUTM
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```


