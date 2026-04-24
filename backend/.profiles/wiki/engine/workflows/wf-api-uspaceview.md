---
title: UspaceView API Workflow
description: Control UspaceView render layers, space regions, camera state, and space/world/screen conversions.
aliases:
  - uspaceview api
  - uspace view usage
  - 3d space region
  - uspaceview에 렌더 레이어 추가
  - uspaceview 카메라 상태 설정
  - uspaceview에 좌표계 설정
  - uspaceview에서 좌표계를 가져오는 방법
  - 공간 좌표를 world 좌표로 바꾸기
  - 공간 좌표를 화면 좌표로 바꾸기
  - 공간 좌표를 world 좌표로 바꾸는 방법
  - 공간 좌표를 화면 좌표로 바꾸는 방법
  - uspace render layer
  - uspace view
symbols:
  - NXUspaceView
  - NXCameraState
  - XSpatialReference
  - NXRenderLayer
tags:
  - engine
  - workflow
  - api
  - uspace
---

# Overview
- Goal: define region, camera, SR, and interaction mode on `NXUspaceView`.
- For the current wiki routing, `UspaceView`-named coordinate or space/screen conversion questions belong here.
- If the question explicitly names `UspaceView`, route here before `Coordinate` or `Sensor Model` for view-owned SR and space/screen conversion APIs.

## Primary Usage Buckets
- `렌더 레이어`: `AddRenderLayer`
- `공간 영역`: `SetSpaceRegion`
- `카메라`: `SetCameraState`
- `좌표계`: `SetSR`, `GetSR`
- `공간/월드/화면 변환`: `SpaceToWorld`, `SpaceToScreen`
- `상호작용`: `SetMouseControlMode`, `GetMouseControlMode`, `GetDrawArgs`

## Practical Answer Shape
- `UspaceView 좌표계`: `SetSR`와 `GetSR`를 먼저 제시하고 Coordinate family와 구분합니다.
- `공간 -> world/screen`: bare conversion 질문이면 `SpaceToWorld` / `SpaceToScreen`을 우선 설명합니다.
- `카메라/영역`: `SetSpaceRegion`과 `SetCameraState`를 같이 묶어 답합니다.


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

## Knowledge Bundle
```yaml
concept_terms:
- render layer
- world mapping
- interaction
routing_hints:
- all_of: [공간 좌표, world 좌표]
- all_of: [공간 좌표, 화면 좌표]
- all_of: [공간 좌표, screen 좌표]
bundle_pages:
- path: pages/howtos/uspaceview-render-and-world.md
  relation: family_howto
- path: pages/concepts/view-screen-world-coordinates.md
  relation: family_concept
- path: pages/sources/nxuspace.md
  relation: source_summary
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-20T02:38:44Z`.
- Resolved required symbols: `11/11`
- Linked modules:
  - `NXUspace`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
```yaml
workflow_family: api_uspaceview
output_shape: workflow_bound_to_host_context
required_symbols:
  - NXUspaceView.AddRenderLayer
  - NXUspaceView.SetSpaceRegion
  - NXUspaceView.SetCameraState
  - NXUspaceView.RefreshScreen
  - NXUspaceView.SetSR
  - NXUspaceView.GetSR
  - NXUspaceView.SpaceToWorld
  - NXUspaceView.SpaceToScreen
  - NXUspaceView.GetDrawArgs
  - NXUspaceView.SetMouseControlMode
  - NXUspaceView.GetMouseControlMode
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```


