---
title: Raster and XDM API Workflow
description: Load raster files, fetch bands, build XDM composites, and tune display enhancement parameters.
aliases:
  - raster api
  - raster load
  - xrasterio usage
  - xdm composite usage
  - geotiff load
  - imageview geotiff display
  - imageview xdm display
  - imageview xdm file load
  - imageview xdm 파일 로드
  - imageview를 이용하여 xdm 파일 로드하여 화면에 도시
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
  - xdm 영상 화질개선
  - xdm 영상 보정
  - imageview 화질개선
  - imageview에서 도시한 영상의 화질개선
  - 도시한 영상의 화질개선
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
- `화질 개선/보정`: `SetCutType`, `SetStretchCoverage`, `SetStretchType`, `SetCutMin`, `SetCutMax`, `SetGammaValue`, `SetBrightness`, `SetContrast`, `SetSaturation`, `SetColorBalance`, `InterpolPixel`, `InterpolByCubic`
- `확대 표시 품질`: `XDMComposite.InterpolPixel`, `XDMComposite.InterpolByCubic`
- `고급 XDM 처리`: `XDMBandHistogramMatching`, `XDMBandImageSharpen`, `XDMBandNoiseInterpol`, `XDMBandGeoCorrect`, `XDMBandEpipolar`, `XDMBandOrthoRPC`, `XDMBandSarS2G`

## Family Boundaries
- If the question is about attaching loaded raster to `NXImageView`, continue with [ImageView API Workflow](wf-api-imageview.md).
- If the question is about vector files, use [Vector API Workflow](wf-api-vector.md).
- Source anchors for this family live in [NXDLio source](../pages/sources/nxdlio.md) and [NXDLrs source](../pages/sources/nxdlrs.md).

## Practical Answer Shape
- `파일 로드`: 기본 XDM/GeoTiff 표시 예제는 짧은 `LoadFile(fileName, out error, calcStatistics, eIOCreateXLDMode.All_NoMsg)` overload를 우선 사용; 확인 안 된 `None`/placeholder enum을 쓰지 않음
- `흑백/칼라 합성`: `SetBand(ref band, (eCompBandIdx)0/1/2)` -> `AddXDMComposite` -> 필요 시 `MoveComposite`; `Red/Green/Blue` enum member는 증거에 없으면 쓰지 않음
- `화질 개선/보정`: 생성/등록 시 보관한 `XDMComposite` 참조에 `SetCutType`, `SetStretchType`, `SetStretchCoverage`, `SetCutMin/Max`, `SetGammaValue`, `SetBrightness`, `SetContrast`, `SetSaturation`, `SetColorBalance`, `InterpolPixel`, `InterpolByCubic`를 적용
- `도시된 영상 보정 코드`: 반드시 `void ApplyDisplayQuality(NXImageView imageView, XDMComposite comp)` 같은 helper 형태로 작성하고, 이미 가진 `XDMComposite`를 파라미터로 받음; `NXImageView` getter나 확인 안 된 manager index getter를 만들지 않음
- `확대 표시 품질`: `InterpolPixel`, `InterpolByCubic`
- `ImageView 표시`: composite를 만든 뒤 `NXImageLayer imageLayer = compLayer as NXImageLayer; imageView.AddImageLayer(ref imageLayer);` 형태로 view attach를 설명

## Display Quality / Enhancement Flow
Use this exact helper shape for questions about improving an already displayed ImageView/XDM image. The composite reference must come from the earlier create/register step; do not invent ImageView or manager getter code to recover it.

```csharp
void ApplyDisplayQuality(NXImageView imageView, XDMComposite comp)
{
    if (imageView == null || comp == null)
        return;

    comp.SetBrightness(brightnessValue);
    comp.SetContrast(contrastValue);
    comp.SetSaturation(saturationValue);
    comp.SetColorBalance(redBalance, greenBalance, blueBalance);
    comp.SetGammaValue(gammaValue, 0);
    comp.InterpolPixel = true;
    comp.InterpolByCubic = true;

    imageView.RefreshScreen();
}
```


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
  any_of: [순서, stretch, cut, 흑백, 칼라, histogram, sharpen, gamma, contrast, 보정, 화질개선]
- all_of: [imageview, xdm]
  any_of: [file, load, display, 로드, 파일, 도시, 표시]
- all_of: [xdm, 파일]
  any_of: [로드, 도시, 표시, imageview]
- all_of: [화질개선]
- all_of: [영상, 보정]
- all_of: [imageview]
  any_of: [화질개선, 보정, stretch, gamma, contrast, interpolation]
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
- Auto-generated from raw source ingest at `2026-04-27T01:07:34Z`.
- Resolved required symbols: `25/25`
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
  - XDMComposite.GetBand
  - XDMComposite.SetGammaValue
  - XDMComposite.GetGammaValue
  - XDMComposite.SetBrightness
  - XDMComposite.SetContrast
  - XDMComposite.SetSaturation
  - XDMComposite.SetColorBalance
  - XDMComposite.InterpolPixel
  - XDMComposite.InterpolByCubic
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


