---
title: PlanetView API Workflow
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
- If `PlanetView` is explicitly named, prefer this family for its shader, camera, render-layer, capture, and dataset-display questions.
- If `PlanetView` is named but the actual task is video channel wiring or embedded video-layer handling, prefer `VideoView`.

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
- Auto-generated from raw source ingest at `2026-04-20T00:52:13Z`.
- Resolved required symbols: `10/10`
- Linked modules:
  - `NXPlanet`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Required Facts
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
required_facts:
  - symbol: NXPlanetView.SetCameraPosition
    declaration: 'bool SetCameraPosition(NXDL::XGeoPoint^ pos, NXDL::XAngle^ azimuth);'
    source: 'Source/NXPlanet/NXPlanetView.h:570'
  - symbol: NXPlanetView.SetCameraState
    declaration: 'bool SetCameraState(NXCameraState^ state);'
    source: 'Source/NXPlanet/NXPlanetView.h:564'
  - symbol: NXPlanetView.AddRenderLayer
    declaration: 'bool AddRenderLayer (NXRenderLayer^% layer);'
    source: 'Source/NXPlanet/NXPlanetView.h:536'
  - symbol: NXPlanetView.ChangeLayerOrder
    declaration: 'bool ChangeLayerOrder(cli::array<NXRenderLayer^>^% layers);'
    source: 'Source/NXPlanet/NXPlanetView.h:768'
  - symbol: NXPlanetView.CaptureScreen
    declaration: 'Bitmap^ CaptureScreen();'
    source: 'Source/NXPlanet/NXPlanetView.h:812'
  - symbol: NXPlanetView.SetPBIDefaultDataSet
    declaration: 'void SetPBIDefaultDataSet(String^ strSource);'
    source: 'Source/NXPlanet/NXPlanetView.h:694'
  - symbol: NXPlanetEngine.AddPBIGroup
    declaration: 'static bool AddPBIGroup(XPBTDataGroup^% Group);'
    source: 'Source/NXPlanet/NXPlanetEngine.h:87'
  - symbol: NXPlanetEngine.RemovePBIGroup
    declaration: 'static bool RemovePBIGroup(int nGroupID);'
    source: 'Source/NXPlanet/NXPlanetEngine.h:92'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```

