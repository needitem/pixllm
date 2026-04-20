---
title: ImageView API Workflow
description: Host NXImageView, attach layers, control view state, and handle composite-linked display tasks.
aliases:
  - imageview api
  - imageview 사용법
  - nximageview usage
  - nximageview wpf hosting
  - windowsformshost nximageview
  - wpf에서 nximageview를 호스팅
  - imageview geotiff display
  - imageview xdm display
  - imageview layer add
  - imageview background map
  - imageview zoom fit
  - imageview pixel read
  - imageview 화면 좌표를 실제 좌표로 바꾸는 방법
  - imageview에 비교용 합성 레이어를 붙이는 방법
  - imageview 합성 관리자 1 가져오기
  - imageview 합성 관리자 2 가져오기
  - imageview에서 합성 1 front 설정
  - imageview에서 합성 2 front 설정
  - 합성 1 front 설정
  - 합성 2 front 설정
symbols:
  - NXImageView
  - NXImageLayer
  - NXImageLayerComposites
  - NXImageLayerCompLink
  - XDMCompManager
  - XDMComposite
tags:
  - engine
  - workflow
  - api
  - imageview
  - wpf
---

# Overview
- Goal: answer most `NXImageView` usage questions from one page.
- Default host context: WPF. `NXImageView` is a WinForms-backed control, so host it through `WindowsFormsHost` when the shell matters.
- This workflow covers host setup, layer attach/remove, background-map configuration, zoom/world control, screen/world conversion, pixel read, and XDM composite hookup.
- For the current wiki routing, treat view-owned operations such as layer attach, background map, zoom, refresh, and ImageView screen/world conversion as `ImageView`; if the question is really about XDM band/composite assembly, route to `Raster`.
- For the current wiki routing, questions about `NXImageLayerCompLink` comp-manager retrieval or composite `1/2 Front` settings stay in `ImageView`; those are documented here as view-owned composite-link operations.
- For the current wiki routing, embedded video-layer channel wiring, channel reset, initial frame size, and video-layer screen/world conversion are handled by `VideoView`.

## Primary Usage Buckets
- `ImageView에 Layer 추가/제거`: `AddImageLayer`, `RemoveImageLayer`, `ClearLayer`
- `파일을 띄운 뒤 화면 맞춤`: `ZoomFit`, `ZoomFitRect`, `ZoomOneToOne`, `RefreshScreen`
- `화면/좌표 변환`: `ScreenToWorld`, `WorldToScreen`, `SetWorld`, `SetWorldToCenter`, `SetWorldPerScreen`
- `배경지도`: `SetBackgroundMap` and related background-map properties
- `XDM / 합성`: `NXImageLayerComposites.GetXDMCompManager`, `ReadPixelValues`, `ZoomFit`
- `특수 레이어`: `NXImageLayerCompLink.GetXDLCompManager1`, `GetXDLCompManager2`, `ZoomFit`

## Family Boundaries
- File load and band extraction live in [Raster API Workflow](wf-api-raster.md).
- If the question is mainly about vector files or overlays, use [Vector API Workflow](wf-api-vector.md).
- Source anchors for this family live in [NXImage source](../pages/sources/nximage.md), [NXDLio source](../pages/sources/nxdlio.md), and [NXDLrs source](../pages/sources/nxdlrs.md).

## Practical Answer Shape
- `ImageView에 레이어 추가`: view 생성/호스팅 -> `AddImageLayer` -> `ZoomFit` 또는 `RefreshScreen`
- `배경지도 설정`: `SetBackgroundMap` 호출과 이후 view refresh를 같이 설명
- `화면/실좌표 변환`: `ScreenToWorld` / `WorldToScreen`을 pair로 설명
- `합성 관리자/comp-link`: `GetXDMCompManager` 또는 `GetXDLCompManager1/2`가 필요한지 먼저 가릅니다


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

## Knowledge Bundle
```yaml
concept_terms:
- layer
- composite
- background map
- screen world transform
routing_hints:
- all_of: [합성, front]
- all_of: [합성 관리자]
- all_of: [imageview, 합성 관리자]
- all_of: [imageview]
  any_of: [layer, 레이어, 배경지도, zoomfit, zoom fit, 픽셀값, 화면 좌표, world 좌표]
bundle_pages:
- path: pages/howtos/imageview-display-recipes.md
  relation: family_howto
- path: pages/concepts/layer-composite-display-pipeline.md
  relation: family_concept
- path: pages/concepts/view-screen-world-coordinates.md
  relation: family_concept
- path: workflows/wf-api-raster.md
  relation: dependency_workflow
- path: pages/sources/nximage.md
  relation: source_summary
- path: pages/sources/nxdlio.md
  relation: source_summary
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-20T02:38:44Z`.
- Resolved required symbols: `20/20`
- Linked modules:
  - `NXImage`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
```yaml
workflow_family: api_imageview
output_shape: workflow_bound_to_host_context
required_symbols:
  - NXImageView.AddImageLayer
  - NXImageView.RemoveImageLayer
  - NXImageView.ClearLayer
  - NXImageView.SetBackgroundMap
  - NXImageView.ZoomFit
  - NXImageView.ZoomOneToOne
  - NXImageView.ZoomFitRect
  - NXImageView.SetWorld
  - NXImageView.SetWorldToCenter
  - NXImageView.SetWorldPerScreen
  - NXImageView.LinkCameraFrom
  - NXImageView.RefreshScreen
  - NXImageView.ScreenToWorld
  - NXImageView.WorldToScreen
  - NXImageLayerComposites.GetXDMCompManager
  - NXImageLayerComposites.ReadPixelValues
  - NXImageLayerComposites.ZoomFit
  - NXImageLayerCompLink.GetXDLCompManager1
  - NXImageLayerCompLink.GetXDLCompManager2
  - NXImageLayerCompLink.ZoomFit
required_facts:
  - symbol: NXImageView.AddImageLayer
    declaration: 'bool AddImageLayer(NXImageLayer^% layer);'
    source: 'Source/NXImage/NXImageView.h:836'
  - symbol: NXImageView.RemoveImageLayer
    declaration: 'bool RemoveImageLayer(NXImageLayer^ layer);'
    source: 'Source/NXImage/NXImageView.h:841'
  - symbol: NXImageView.ClearLayer
    declaration: 'void ClearLayer();'
    source: 'Source/NXImage/NXImageView.h:112'
  - symbol: NXImageView.SetBackgroundMap
    declaration: 'bool SetBackgroundMap(String^ strConfig);'
    source: 'Source/NXImage/NXImageView.h:356'
  - symbol: NXImageView.ZoomFit
    declaration: 'bool ZoomFit();'
    source: 'Source/NXImage/NXImageView.h:198'
  - symbol: NXImageView.ZoomOneToOne
    declaration: 'bool ZoomOneToOne();'
    source: 'Source/NXImage/NXImageView.h:206'
  - symbol: NXImageView.ZoomFitRect
    declaration: 'bool ZoomFitRect(double llx, double lly, double urx, double ury);'
    source: 'Source/NXImage/NXImageView.h:219'
  - symbol: NXImageView.SetWorld
    declaration: 'bool SetWorld(XVertex2d^ vCenter, XVertex2d^ vPixelSize, XAngle^ aRotate);'
    source: 'Source/NXImage/NXImageView.h:235'
  - symbol: NXImageView.SetWorldToCenter
    declaration: 'bool SetWorldToCenter(double wcx, double wcy);'
    source: 'Source/NXImage/NXImageView.h:241'
  - symbol: NXImageView.SetWorldPerScreen
    declaration: 'bool SetWorldPerScreen(double wpx, double wpy);'
    source: 'Source/NXImage/NXImageView.h:253'
  - symbol: NXImageView.LinkCameraFrom
    declaration: 'bool LinkCameraFrom(NXImageView^ view);'
    source: 'Source/NXImage/NXImageView.h:224'
  - symbol: NXImageView.RefreshScreen
    declaration: 'bool RefreshScreen();'
    source: 'Source/NXImage/NXImageView.h:228'
  - symbol: NXImageLayerComposites.GetXDMCompManager
    declaration: 'XDMCompManager^ GetXDMCompManager();'
    source: 'Source/NXImage/NXImageLayerComposites.h:149'
  - symbol: NXImageLayerComposites.ZoomFit
    declaration: 'bool ZoomFit();'
    source: 'Source/NXImage/NXImageLayerComposites.h:142'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```


