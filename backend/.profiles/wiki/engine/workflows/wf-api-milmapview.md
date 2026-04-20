---
title: MilmapView API Workflow
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
- If `MilmapView` is explicitly named, prefer this family for its shader, render-layer, capture, and display questions even when raster terms also appear.
- If `MilmapView` is named but the actual task is video channel wiring, video-layer setup, KLV, or frame capture, prefer `VideoView`.

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
- Auto-generated from raw source ingest at `2026-04-20T00:52:13Z`.
- Resolved required symbols: `13/13`
- Linked modules:
  - `NXMilmap`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Required Facts
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
required_facts:
  - symbol: NXMilmapView.CheckMilmapData
    declaration: 'bool CheckMilmapData(XVertex2d^ vGeo, int nScaleIndex);'
    source: 'Source/NXMilmap/NXMilmapView.h:110'
  - symbol: NXMilmapView.SetGeoToCenter
    declaration: 'bool SetGeoToCenter(int nScaleIndex, XVertex2d^ vGeo);'
    source: 'Source/NXMilmap/NXMilmapView.h:116'
  - symbol: NXMilmapView.SearchScale
    declaration: 'int SearchScale(String^ m);'
    source: 'Source/NXMilmap/NXMilmapView.h:125'
  - symbol: NXMilmapView.Zoom
    declaration: 'bool Zoom(int scaleIndex, double factor);'
    source: 'Source/NXMilmap/NXMilmapView.h:131'
  - symbol: NXMilmapView.ZoomFitRect
    declaration: 'bool ZoomFitRect(int scaleIndex, double llx, double lly, double urx, double ury, bool bAuto);'
    source: 'Source/NXMilmap/NXMilmapView.h:141'
  - symbol: NXMilmapView.AddRenderLayer
    declaration: 'bool AddRenderLayer(NXMilmapLayer^% layer);'
    source: 'Source/NXMilmap/NXMilmapView.h:165'
  - symbol: NXMilmapView.ChangeLayerOrder
    declaration: 'bool ChangeLayerOrder(cli::array<NXRenderLayer^>^% layers);'
    source: 'Source/NXMilmap/NXMilmapView.h:231'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```

