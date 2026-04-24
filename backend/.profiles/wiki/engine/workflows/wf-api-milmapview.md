---
title: MilmapView API Workflow
description: Control MilmapView scale, center, render layers, capture, and map display state.
aliases:
  - milmapview api
  - milmapview 사용법
  - milmap scale
  - milmap capture
  - milmapview에서 xdm 합성 추가하는 방법
  - milmapview에서 shader code cbs 사용하는 방법
  - milmapview에서 shader code basso 사용하는 방법
  - milmapview cartoon effect
symbols:
  - NXMilmapView
  - NXMilmapLayer
  - NXMilmapLayerComposites
  - NXRenderLayer
tags:
  - engine
  - workflow
  - api
  - milmap
---

# Overview
- Goal: cover scale, center, render-layer attach/order, draw args, and capture on `NXMilmapView`.
- This workflow is the primary family for normal `MilmapView` usage questions.
- For the current wiki routing, if `MilmapView` is explicitly named, this family covers shader, render-layer, capture, and display questions even when raster terms also appear.
- For the current wiki routing, if `MilmapView` is named but the actual task is video channel wiring, video-layer setup, KLV, or frame capture, route to `VideoView`.

## Primary Usage Buckets
- `축척/위치`: `SearchScale`, `SearchName`, `SetGeoToCenter`, `Zoom`, `ZoomFitRect`, `CalculateScale`
- `표시 확인`: `CheckMilmapData`, `IsExistScale`, `ShowCross`, `RefreshScreen`
- `레이어 관리`: `AddRenderLayer`, `RemoveRenderLayer`, `ChangeLayerOrder`, `GetLayerOrder`
- `캡처와 draw args`: `CaptureScreen`, `GetDrawArgs`
- `성능/보기 상태`: `EnableControlRatio`, `FreezeViewArea`, `SetResolutionThreshold`, `SetViewZoomCenterPosition`

## Practical Answer Shape
- `Milmap 데이터가 있는지 확인`: `CheckMilmapData`와 `IsExistScale`를 먼저 설명합니다.
- `특정 중심/축척으로 이동`: `SearchScale` -> `SetGeoToCenter` -> `Zoom` 흐름으로 답합니다.
- `레이어 순서 변경`: `AddRenderLayer` 후 `ChangeLayerOrder` 또는 `GetLayerOrder`를 같이 제시합니다.


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

## Knowledge Bundle
```yaml
concept_terms:
- map view
- layer display
- video layer
- world mapping
bundle_pages:
- path: pages/howtos/milmapview-display-and-video.md
  relation: family_howto
- path: pages/concepts/view-screen-world-coordinates.md
  relation: family_concept
- path: pages/concepts/provider-dataset-and-scene-assets.md
  relation: family_concept
- path: workflows/wf-api-raster.md
  relation: dependency_workflow
- path: pages/sources/nxmilmap.md
  relation: source_summary
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-20T02:38:44Z`.
- Resolved required symbols: `13/13`
- Linked modules:
  - `NXMilmap`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
```yaml
workflow_family: api_milmapview
output_shape: workflow_bound_to_host_context
required_symbols:
  - NXMilmapView.CheckMilmapData
  - NXMilmapView.SetGeoToCenter
  - NXMilmapView.SearchScale
  - NXMilmapView.Zoom
  - NXMilmapView.ZoomFitRect
  - NXMilmapView.IsExistScale
  - NXMilmapView.SearchName
  - NXMilmapView.ShowCross
  - NXMilmapView.RefreshScreen
  - NXMilmapView.AddRenderLayer
  - NXMilmapView.ChangeLayerOrder
  - NXMilmapView.GetDrawArgs
  - NXMilmapView.CaptureScreen
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```


