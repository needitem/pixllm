---
title: UspaceView API Workflow
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
- Prefer this family for `UspaceView`-named coordinate or space/screen conversion questions.
- If the question explicitly names `UspaceView`, prefer this family over `Coordinate` or `Sensor Model` for view-owned SR and space/screen conversion APIs.

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
- Auto-generated from raw source ingest at `2026-04-20T00:52:13Z`.
- Resolved required symbols: `11/11`
- Linked modules:
  - `NXUspace`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Required Facts
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
required_facts:
  - symbol: NXUspaceView.AddRenderLayer
    declaration: 'bool AddRenderLayer (NXRenderLayer^% layer);'
    source: 'Source/NXUspace/NXUspaceView.h:87'
  - symbol: NXUspaceView.SetSpaceRegion
    declaration: 'void SetSpaceRegion(XVertex2d^ vMinSpace, XVertex2d^ vMaxSpace, XVertex2d^ vPsz);'
    source: 'Source/NXUspace/NXUspaceView.h:93'
  - symbol: NXUspaceView.SetCameraState
    declaration: 'void SetCameraState(XVertex3d^ vEye, XVertex3d^ vLookAt, XVertex3d^ vUp);'
    source: 'Source/NXUspace/NXUspaceView.h:99'
  - symbol: NXUspaceView.RefreshScreen
    declaration: 'void RefreshScreen();'
    source: 'Source/NXUspace/NXUspaceView.h:106'
  - symbol: NXUspaceView.SetSR
    declaration: 'void SetSR(NCC::XSpatialReference^ sr);'
    source: 'Source/NXUspace/NXUspaceView.h:110'
  - symbol: NXUspaceView.GetSR
    declaration: 'NCC::XSpatialReference^ GetSR();'
    source: 'Source/NXUspace/NXUspaceView.h:114'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```

