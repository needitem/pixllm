---
title: Vector API Workflow
aliases:
  - vector api
  - vector file load
  - xvectorio usage
  - vector overlay
  - imageview vector overlay
  - imageview 위에 shp overlay
  - 벡터 객체 속성 이름과 값을 읽기
  - polyline polygon에 vertex 추가
  - vector object properties
  - shp overlay
  - 벡터 파일의 bounding box와 좌표계를 확인하는 방법
  - 점 벡터 객체의 좌표를 설정하는 방법
  - 벡터 레이어를 hit test 하는 방법
  - 벡터 데이터를 이미지 위에 같이 도시하는 방법
  - 벡터 로딩 전에 io를 초기화하는 방법
  - imageview 위에 shp를 overlay 하는 방법
  - 벡터 파일의 driver key 확인
  - 벡터 파일 export extension 지원 확인
  - 벡터 파일 사용법
  - 벡터 파일 filters for load 확인
  - 벡터 파일 filters for save 확인
symbols:
  - XVectorIO
  - XvcBase
  - XvcObj
  - XvcPoint
  - XvcLine
  - XvcPolyline
  - XvcPolygon
  - XvcLayer
  - NXImageView
tags:
  - engine
  - workflow
  - api
  - vector
---

# Overview
- Goal: load vector data, inspect metadata, create vector objects, and overlay them on image or map views.
- Prefer this family for `vector`, `shp`, `overlay`, `bounding box`, `vertex`, `property`, and vector-layer hit-test questions even when ImageView is also mentioned.
- If the question mentions vector file metadata, driver key, supported extensions, vector bounds, or vector geometry setup, prefer this family over `Coordinate` or `ImageView`.

## Knowledge Bundle
```yaml
concept_terms:
- vector overlay
- geometry bounds
- dataset coordinates
bundle_pages:
- path: pages/howtos/vector-load-and-overlay.md
  relation: family_howto
- path: pages/concepts/spatial-reference-and-coordinate-transform.md
  relation: family_concept
- path: workflows/wf-api-coordinate.md
  relation: dependency_workflow
- path: pages/sources/nxdlio.md
  relation: source_summary
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-20T00:52:13Z`.
- Resolved required symbols: `11/11`
- Linked modules:
  - `NXDLio`
  - `NXDLvc`
  - `NXImage`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Required Facts
```yaml
workflow_family: api_vector
output_shape: focused_snippet_or_helper
required_symbols:
  - XVectorIO.Initialize
  - XVectorIO.LoadFile
  - XVectorIO.GetFileInfo
  - XvcObj.GetPropertyNameAt
  - XvcObj.GetPropertyValueAt
  - XvcPoint.SetVertex
  - XvcLine.SetVertices
  - XvcPolyline.Add
  - XvcPolygon.Add
  - XvcLayer.HitTest
  - NXImageView.AddImageLayer
required_facts:
  - symbol: XVectorIO.Initialize
    declaration: 'bool Initialize([OutAttribute] String^% strError);'
    source: 'Source/NXDLio/NXDLio.h:802'
  - symbol: XVectorIO.LoadFile
    declaration: 'NVC::XvcBase^ LoadFile(String^ strFileName, [OutAttribute] String^% strError, NCC::XSpatialReference^% pInSR);'
    source: 'Source/NXDLio/NXDLio.h:824'
  - symbol: XVectorIO.GetFileInfo
    declaration: 'bool GetFileInfo(String^ strFileName, double% minx, double% miny, double% minz, double% maxx, double% maxy, double% maxz, NCC::XSpatialReference^% sr);'
    source: 'Source/NXDLio/NXDLio.h:865'
  - symbol: XvcObj.GetPropertyNameAt
    declaration: 'String^ GetPropertyNameAt(int idx);'
    source: 'Source/NXDLvc/NXDLvc.h:233'
  - symbol: XvcObj.GetPropertyValueAt
    declaration: 'String^ GetPropertyValueAt(int idx);'
    source: 'Source/NXDLvc/NXDLvc.h:234'
  - symbol: XvcPoint.SetVertex
    declaration: 'void SetVertex(double x, double y, double z);'
    source: 'Source/NXDLvc/NXDLvc.h:349'
  - symbol: XvcLine.SetVertices
    declaration: 'void SetVertices(double x1, double y1, double z1, double x2, double y2, double z2);'
    source: 'Source/NXDLvc/NXDLvc.h:411'
  - symbol: XvcPolyline.Add
    declaration: 'void Add(double x, double y, double z);'
    source: 'Source/NXDLvc/NXDLvc.h:572'
  - symbol: XvcPolygon.Add
    declaration: 'void Add(double x, double y, double z);'
    source: 'Source/NXDLvc/NXDLvc.h:945'
  - symbol: XvcLayer.HitTest
    declaration: 'bool HitTest(double x, double y, double tol, [OutAttribute] ArrayList^% results);'
    source: 'Source/NXDLvc/NXDLvc.h:1341'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```

