---
title: Sensor Model API Workflow
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
- Prefer this family for image-to-ground, ground-to-image, image-to-geo, geo-to-image, and image-center map-coordinate questions.

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
- Auto-generated from raw source ingest at `2026-04-20T00:52:13Z`.
- Resolved required symbols: `7/7`
- Linked modules:
  - `NXDLsm`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Required Facts
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
required_facts:
  - symbol: XFrameSensor.SetParamsLocal
    declaration: 'bool SetParamsLocal(XFrameSensorParams^ param);'
    source: 'Source/NXDLsm/NXDLsm.h:273'
  - symbol: XFrameSensor.SetParamsEarth
    declaration: 'bool SetParamsEarth(XFrameSensorParams^ param);'
    source: 'Source/NXDLsm/NXDLsm.h:268'
  - symbol: XSensorModel.WorldToImageE
    declaration: 'virtual bool WorldToImageE(NXDL::XVertex3d^ ptEuc, [OutAttribute] XVertex2d^% ptImg);'
    source: 'Source/NXDLsm/NXDLsm.h:57'
  - symbol: XSensorModel.ImageToWorldE
    declaration: 'virtual bool ImageToWorldE(XVertex2d^ ptImg, double hEuc, [OutAttribute] NXDL::XVertex3d^% ptEuc);'
    source: 'Source/NXDLsm/NXDLsm.h:64'
  - symbol: XSensorModel.WorldToImageG
    declaration: 'virtual bool WorldToImageG(NXDL::XVertex3d^ ptGeo,[OutAttribute] NXDL::XVertex2d^% ptImg);'
    source: 'Source/NXDLsm/NXDLsm.h:70'
  - symbol: XSensorModel.ImageToWorldG
    declaration: 'virtual bool ImageToWorldG(NXDL::XVertex2d^ ptImg, const double hGeo, [OutAttribute] NXDL::XVertex3d^% ptGeo);'
    source: 'Source/NXDLsm/NXDLsm.h:77'
  - symbol: XSensorModel.GetMapCoordOfImageCenter
    declaration: 'virtual NXDL::XVertex3d^ GetMapCoordOfImageCenter();'
    source: 'Source/NXDLsm/NXDLsm.h:81'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```

