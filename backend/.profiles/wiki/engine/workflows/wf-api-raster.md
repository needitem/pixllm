---
title: Raster and XDM API Workflow
description: Load raster files, fetch bands, build XDM composites, and tune display enhancement parameters.
aliases:
  - raster api
  - raster load
  - xrasterio usage
  - xdm composite usage
  - geotiff load
  - xdm band display
  - grayscale rgb composite
  - raster enhance
  - raw raster load
  - xdm histogram matching
  - xdm sharpen
  - xdm composite order
  - geotiff 파일을 xrasterio로 로드
  - xdm 파일을 로드해서 밴드를 가져오기
  - 래스터 파일의 subdataset 목록 확인
  - raw raster 파일을 loadrawfile로 읽기
  - 입력한 파일 밴드 수에 따라 흑백 또는 칼라로 도시
  - xdm 영상 히스토그램 매칭
  - xdm 영상 샤프닝
  - xdm 합성 순서 변경
  - xdm composite를 추가하는 방법
  - xdm stretch와 cut 값을 조정하는 방법
  - xdm composite 추가
  - xdm composite 이동 제거
symbols:
  - XRasterIO
  - XVectorIO
  - Xio
  - XRSLoadFile
  - XDMBand
  - XDMBand2DMem
  - XDMBandAffineTransform
  - XDMBandChangeDetect
  - XDMBandChangeDetectSig
  - XDMBandChangeDetectSpecAng
  - XDMBandComplex
  - XDMBandConvDataType
  - XDMBandData2Binary
  - XDMBandData2GIS
  - XDMBandEOIR
  - XDMBandEnhance
  - XDMBandEpipolar
  - XDMBandEpipolarDEM
  - XDMBandFeatureExt
  - XDMBandFlip
  - XDMBandFusion
  - XDMBandGeoCorrect
  - XDMBandHDRC
  - XDMComposite
  - XDMCompManager
  - XDMBandHistogramMatching
  - XDMBandIRFilter2
  - Xio
  - XDMBandImageSharpen
  - XDMBandIndexTransform
  - XDMBandLandCover2GIS
  - XDMBandLocalWarp
  - XDMBandMapConv
  - XDMBandMask
  - XDMBandMath
  - XDMBandMosaic
  - XDMBandMosaicLT
  - XDMBandHistogramMatching
  - XDMBandImageSharpen
  - XDMBandNoiseInterpol
  - XDMBandOrthoFrame
  - XDMBandOrthoRPC
  - XDMBandPointsToGrid
  - XDMBandRegionGen
  - XDMBandResize
  - XDMBandRiverDetect
  - XDMBandRotate
  - XDMBandSarS2G
  - XDMBandShadowEnhance
  - XDMBandSpatialFilter
  - XDMBandSuperClass
  - XDMBandTileMerge
  - XDMBandTopoModel
  - XDMBandUnSuperClass
  - XDMBandGeoCorrect
  - XDMBandEpipolar
  - XDMBandOrthoRPC
  - XDMBandSarS2G
tags:
  - engine
  - workflow
  - api
  - raster
  - xdm
---

# Overview
- Goal: cover raster-file load, band access, XDM composite assembly, and display-quality tuning.
- This workflow is the primary family for `XRasterIO`, `XRSLoadFile`, `XDMBand`, `XDMComposite`, and `XDMCompManager`.
- Prefer this family for XDM composite add/move/remove, grayscale/RGB composition, and raster stretch/cut/enhancement; prefer `ImageView` only for the view shell and layer attachment.
- Do not steal `ImageView` comp-link manager retrieval or composite `1/2 Front` settings; those stay in `ImageView`.

## Primary Usage Buckets
- `파일 로드`: `Initialize`, `LoadFile`, `GetSubDatasets`, `LoadRawFile`, `GetFileInfo`
- `밴드 접근`: `XRSLoadFile.GetBandAt`
- `흑백/칼라 도시`: `XDMComposite.SetBand`, `XDMCompManager.AddXDMComposite`
- `합성 순서/선택`: `MoveComposite`, `RemoveXDMComposite*`, `HitTest`
- `화질 조정`: `SetCutType`, `SetStretchCoverage`, `SetStretchType`, `SetCutMin`, `SetCutMax`
- `고급 XDM 처리`: `XDMBandHistogramMatching`, `XDMBandImageSharpen`, `XDMBandNoiseInterpol`, `XDMBandGeoCorrect`, `XDMBandEpipolar`, `XDMBandOrthoRPC`, `XDMBandSarS2G`

## Family Boundaries
- If the question is about attaching loaded raster to `NXImageView`, continue with [ImageView API Workflow](wf-api-imageview.md).
- If the question is about vector files, use [Vector API Workflow](wf-api-vector.md).
- Source anchors for this family live in [NXDLio source](../pages/sources/nxdlio.md) and [NXDLrs source](../pages/sources/nxdlrs.md).

## Practical Answer Shape
- `파일 로드`: `Initialize` -> `LoadFile`/`LoadRawFile` -> `GetSubDatasets` or `GetBandAt`
- `흑백/칼라 합성`: `SetBand` -> `AddXDMComposite` -> 필요 시 `MoveComposite`
- `화질 조정`: `SetCutType`, `SetStretchType`, `SetStretchCoverage`, `SetCutMin/Max`
- `ImageView 표시`: composite를 만든 뒤 `ImageView` workflow로 넘겨 최종 view attach를 설명


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

## Knowledge Bundle
```yaml
concept_terms:
- band
- composite
- stretch
- enhancement
routing_hints:
- all_of: [xdm, 합성]
  any_of: [순서, stretch, cut, 흑백, 칼라, histogram, sharpen]
- all_of: [raster]
  any_of: [band, subdataset, loadrawfile, geotiff]
bundle_pages:
- path: pages/howtos/raster-load-and-composite.md
  relation: family_howto
- path: pages/howtos/raster-low-level-parameter-recipes.md
  relation: family_howto
- path: pages/concepts/raster-band-and-enhancement.md
  relation: family_concept
- path: pages/concepts/raster-operator-parameter-families.md
  relation: family_concept
- path: pages/concepts/layer-composite-display-pipeline.md
  relation: family_concept
- path: workflows/wf-api-imageview.md
  relation: dependency_workflow
- path: pages/sources/nxdlio.md
  relation: source_summary
- path: pages/sources/nxdlrs.md
  relation: source_summary
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-24T01:05:26Z`.
- Resolved required symbols: `16/16`
- Linked modules:
  - `NXDLio`
  - `NXDLrs`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
```yaml
workflow_family: api_raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XRasterIO.Initialize
  - XRasterIO.LoadFile
  - XRasterIO.GetSubDatasets
  - XRasterIO.LoadRawFile
  - XRasterIO.GetFileInfo
  - XRSLoadFile.GetBandAt
  - XDMComposite.SetBand
  - XDMComposite.SetCutType
  - XDMComposite.SetCutMin
  - XDMComposite.SetCutMax
  - XDMComposite.SetStretchCoverage
  - XDMComposite.SetStretchType
  - XDMCompManager.AddXDMComposite
  - XDMCompManager.RemoveXDMCompositeAll
  - XDMCompManager.MoveComposite
  - XDMCompManager.HitTest
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```


