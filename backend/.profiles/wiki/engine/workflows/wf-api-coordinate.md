---
title: Coordinate API Workflow
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
- Prefer this family for SR/code conversion and explicit coordinate-system transforms, not for sensor-model projection or image-center map-coordinate questions.
- If the question is generic `좌표변환`, `좌표 한 점 변환`, or `두 좌표계 사이 변환` without image/ground projection words, prefer this family.

# Primary Usage Buckets
- `좌표 코드 변환`: `WGP2UTM`, `UTM2WGP`, `WGP2MGRS`, `MGRS2WGP`, `WGP2GEOREF`, `GEOREF2WGP`
- `좌표 한 점 변환`: `CreateCoordinateTransform`, `TransformPt`
- `좌표계 생성/내보내기`: `ImportFromEPSG`, `ImportFromWkt`, `ImportFromProj4`, `ExportToWkt`, `ExportToPrettyWkt`, `ExportToProj4`
- `좌표계 판별`: `IsGeographic`, `IsProjected`, `IsUTM`, `GetUTMZone`, `GetAreaOfUse`, `IsSame`

# Related Sources
- [NXDLcc source](../pages/sources/nxdlcc.md)

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
- Auto-generated from raw source ingest at `2026-04-20T00:52:13Z`.
- Resolved required symbols: `17/17`
- Linked modules:
  - `NXDLcc`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Required Facts
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
required_facts:
  - symbol: Xcc.WGP2UTM
    declaration: 'static bool WGP2UTM(NXDL::XAngle^ lon, NXDL::XAngle^ lat, NXDL::XVertex2d^% pos, int% Zone);'
    source: 'Source/NXDLcc/NXDLcc.h:344'
  - symbol: Xcc.UTM2WGP
    declaration: 'static bool UTM2WGP(NXDL::XVertex2d^ pos, int Zone, NXDL::XAngle^% lon, NXDL::XAngle^% lat);'
    source: 'Source/NXDLcc/NXDLcc.h:464'
  - symbol: Xcc.WGP2MGRS
    declaration: 'static bool WGP2MGRS(NXDL::XAngle^ lon, NXDL::XAngle^ lat, String^% strMGRS);'
    source: 'Source/NXDLcc/NXDLcc.h:419'
  - symbol: Xcc.MGRS2UTM
    declaration: 'static bool MGRS2UTM(String^ strMGRS, NXDL::XVertex2d^% pos, int% Zone);'
    source: 'Source/NXDLcc/NXDLcc.h:522'
  - symbol: Xcc.MGRS2WGP
    declaration: 'static bool MGRS2WGP(String^ strMGRS, NXDL::XAngle^% lon, NXDL::XAngle^% lat);'
    source: 'Source/NXDLcc/NXDLcc.h:541'
  - symbol: XCoordinateTransformation.CreateCoordinateTransform
    declaration: 'bool CreateCoordinateTransform(XSpatialReference^% SrIn, XSpatialReference^% SrOut);'
    source: 'Source/NXDLcc/NXDLcc.h:291'
  - symbol: XCoordinateTransformation.TransformPt
    declaration: 'bool TransformPt(double xIn, double yIn, double% xOut, double% yOut);'
    source: 'Source/NXDLcc/NXDLcc.h:301'
  - symbol: XSpatialReference.GetUTMZone
    declaration: 'int GetUTMZone();'
    source: 'Source/NXDLcc/NXDLcc.h:194'
  - symbol: XSpatialReference.IsUTM
    declaration: 'bool IsUTM();'
    source: 'Source/NXDLcc/NXDLcc.h:183'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```

