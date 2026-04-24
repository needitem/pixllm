---
title: PlanetView API Workflow
description: Control PlanetView camera, render layers, dataset display, and capture operations.
aliases:
  - planetview api
  - planetview 사용법
  - planet view camera
  - planet dataset
  - planet render layer
  - planetview에서 shader code average 사용하는 방법
  - planetview에서 shader code basso 사용하는 방법
  - planetview에서 shader code edge 사용하는 방법
  - planetview에서 shader code median 사용하는 방법
  - planetview cartoon effect
  - sun follow 카메라 설정
symbols:
  - NXPlanetView
  - NXPlanetLayer
  - NXPlanetLayerComposites
  - NXPlanetEngine
  - XPBTDataGroup
  - NXCameraState
  - NXRenderLayer
tags:
  - engine
  - workflow
  - api
  - planet
---

# Overview
- Goal: cover camera, layer attach/order, capture, and dataset registration on `NXPlanetView`.
- This workflow merges view control and PBI dataset usage into one API family page.
- For the current wiki routing, if `PlanetView` is explicitly named, this family covers shader, camera, render-layer, capture, and dataset-display questions.
- For the current wiki routing, if `PlanetView` is named but the actual task is video channel wiring or embedded video-layer handling, route to `VideoView`.

## Primary Usage Buckets
- `카메라 상태`: `SetCameraPosition`, `SetCameraState`, `GetCameraState`, `LookTarget`
- `레이어 관리`: `AddRenderLayer`, `RemoveRenderLayer`, `ChangeLayerOrder`, `GetLayerOrder`
- `화면/월드/지리 좌표`: `ScreenToWorld`, `WorldToScreen`, `GeographicToWorld`, `GeographicToScreen`
- `캡처`: `CaptureScreen`, `CaptureScreenByBlock`
- `렌더/갱신`: `RefreshScreen`, `RefreshBaseMap`, `RefreshLOD`, `RequestRender`
- `데이터셋`: `SetPBIDefaultDataSet`, `SetPBEDefaultDataSet`, `UpdatePBPDataSet`, `UpdatePBVDataSet`
- `환경/카메라 효과`: `SetMouseControlMode`, `SetSunFollowCamera`, `SetSunPosition`, `SetLightingFactor`

## Practical Answer Shape
- `PBI group 등록/기본 dataset`: `NXPlanetEngine.AddPBIGroup`와 `SetPBIDefaultDataSet`을 구분해서 설명합니다.
- `카메라 이동`: `SetCameraPosition`과 `SetCameraState`를 언제 쓰는지 먼저 나눕니다.
- `캡처/블록 캡처`: 전체 화면 저장인지, 블록 캡처인지에 따라 `CaptureScreen` / `CaptureScreenByBlock`을 나눠 답합니다.


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

## Knowledge Bundle
```yaml
concept_terms:
- dataset
- provider
- camera
- scene layer
bundle_pages:
- path: pages/howtos/planetview-dataset-and-camera.md
  relation: family_howto
- path: pages/concepts/provider-dataset-and-scene-assets.md
  relation: family_concept
- path: workflows/wf-api-dfs.md
  relation: dependency_workflow
- path: pages/sources/nxplanet.md
  relation: source_summary
- path: pages/sources/nxdldfs.md
  relation: source_summary
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-24T01:05:26Z`.
- Resolved required symbols: `10/10`
- Linked modules:
  - `NXPlanet`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
```yaml
workflow_family: api_planetview
output_shape: workflow_bound_to_host_context
required_symbols:
  - NXPlanetView.SetCameraPosition
  - NXPlanetView.SetCameraState
  - NXPlanetView.AddRenderLayer
  - NXPlanetView.ChangeLayerOrder
  - NXPlanetView.GetDrawArgs
  - NXPlanetView.CaptureScreen
  - NXPlanetView.SetMouseControlMode
  - NXPlanetView.SetPBIDefaultDataSet
  - NXPlanetEngine.AddPBIGroup
  - NXPlanetEngine.RemovePBIGroup
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```


