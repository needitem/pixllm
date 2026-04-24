---
title: Vector API Workflow
description: Load vector files, inspect vector metadata, create geometry objects, and overlay them onto views.
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
- For the current wiki routing, `vector`, `shp`, `overlay`, `bounding box`, `vertex`, `property`, and vector-layer hit-test questions stay in this family even when ImageView is also mentioned.
- For the current wiki routing, vector file metadata, driver key, supported extensions, vector bounds, or vector geometry setup route here rather than `Coordinate` or `ImageView`.

## Primary Usage Buckets
- `벡터 파일 로드`: `Initialize`, `LoadFile`, `GetFileInfo`
- `파일 메타데이터`: bounding box, spatial reference, driver key, supported extension
- `객체/속성`: `GetPropertyNameAt`, `GetPropertyValueAt`
- `기하 생성`: `SetVertex`, `SetVertices`, `Add`
- `overlay / hit test`: `HitTest`, view layer attach

## Practical Answer Shape
- `벡터 파일 로드`: 먼저 `Initialize` -> `LoadFile` -> 필요한 경우 `GetFileInfo` 순서로 답합니다.
- `속성 확인`: object property name/value access와 geometry setup를 분리해서 설명합니다.
- `overlay`: vector를 로드한 뒤 어느 view에 붙일지 다음 workflow를 연결해줍니다.
- `기하 생성`: point/line/polyline/polygon을 각각 다른 메서드군으로 설명합니다.


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

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
- Auto-generated from raw source ingest at `2026-04-24T01:05:26Z`.
- Resolved required symbols: `11/11`
- Linked modules:
  - `NXDLio`
  - `NXDLvc`
  - `NXImage`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
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
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```


