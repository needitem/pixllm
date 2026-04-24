---
title: Sensor Model API Workflow
description: Configure sensor parameters and project between image, world, and geographic coordinates.
aliases:
  - sensor model api
  - sensor model usage
  - frame sensor usage
  - image world projection
  - sensor model 파라미터 local 기준 설정
  - sensor model 파라미터 earth 기준 설정
  - 지상 좌표를 영상 좌표로 투영
  - 영상 좌표를 지상 좌표로 역투영
  - 지리 좌표를 영상 좌표로 변환
  - 영상 좌표를 지리 좌표로 변환
  - 영상 중심점의 지도 좌표를 얻기
  - world to image projection
  - image to world projection
  - sensor model 기반 위치 투영을 구현하는 방법
  - image center map coordinate
  - 영상 중심점의 지도 좌표를 얻는 방법
symbols:
  - XFrameSensor
  - XFrameSensorParams
  - XSensorModel
  - XRpc
  - XSarSensor
tags:
  - engine
  - workflow
  - api
  - sensor
---

# Overview
- Goal: configure sensor parameters and project between image and world spaces.
- For the current wiki routing, image-to-ground, ground-to-image, image-to-geo, geo-to-image, and image-center map-coordinate questions are handled by this family.

## Primary Usage Buckets
- `sensor 파라미터`: `SetParamsLocal`, `SetParamsEarth`
- `world/image`: `WorldToImageE`, `ImageToWorldE`
- `geo/image`: `WorldToImageG`, `ImageToWorldG`
- `중심점`: `GetMapCoordOfImageCenter`

## Practical Answer Shape
- `영상 좌표 <-> 지상/지리 좌표`: 유클리드(`E`)와 지리(`G`) 경로를 구분해서 설명합니다.
- `sensor 파라미터 설정`: local 기준과 earth 기준을 먼저 나눕니다.
- `영상 중심점`: `GetMapCoordOfImageCenter`를 별도 질문 패턴으로 바로 연결합니다.


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

## Knowledge Bundle
```yaml
concept_terms:
- projection
- image to ground
- sensor geometry
routing_hints:
- all_of: [영상 중심점, 지도 좌표]
- all_of: [image center, map coordinate]
bundle_pages:
- path: pages/howtos/sensor-model-image-ground-projection.md
  relation: family_howto
- path: pages/concepts/sensor-model-and-projection.md
  relation: family_concept
- path: workflows/wf-api-coordinate.md
  relation: dependency_workflow
- path: pages/sources/nxdlsm.md
  relation: source_summary
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-20T02:38:44Z`.
- Resolved required symbols: `7/7`
- Linked modules:
  - `NXDLsm`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
```yaml
workflow_family: api_sensor_model
output_shape: focused_snippet_or_helper
required_symbols:
  - XFrameSensor.SetParamsLocal
  - XFrameSensor.SetParamsEarth
  - XSensorModel.WorldToImageE
  - XSensorModel.ImageToWorldE
  - XSensorModel.WorldToImageG
  - XSensorModel.ImageToWorldG
  - XSensorModel.GetMapCoordOfImageCenter
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```


