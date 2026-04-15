---
title: Raster Vector Overlay Workflow
aliases:
  - Raster Vector Overlay Workflow
  - wf-raster-vector-overlay
  - wf raster vector overlay
symbols:
  - XVectorIO
  - XvcBase
  - NXImageView
  - NXImageLayerVectorDisplay
  - NXImageLayerVectorEditor
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Load vector data and overlay it on raster/image views.
- Core calls:
  - `XVectorIO.Initialize`
  - `XVectorIO.GetFileInfo`
  - `XVectorIO.LoadFile`
  - `NXImageView.AddImageLayer`
- Verified source:
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
  - `Source/NXImage/NXImageView.h:836`
- Steps:
  - 벡터 IO를 초기화한다.
  - 필요 시 메타정보를 읽는다.
  - 벡터 파일을 로드하고 벡터 레이어를 뷰에 붙인다.


## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XVectorIO.Initialize
  - XVectorIO.GetFileInfo
  - XVectorIO.LoadFile
  - NXImageView.AddImageLayer
required_facts:
  - symbol: XVectorIO.Initialize
    declaration: 'bool		Initialize([OutAttribute] String^% strError);'
    source: 'Source/NXDLio/NXDLio.h:802'
  - symbol: XVectorIO.GetFileInfo
    declaration_candidates:
      - declaration: 'bool GetFileInfo(String^ strFileName, double% minx, double% miny, double% minz, double% maxx, double% maxy, double% maxz, NCC::XSpatialReference^% sr);'
        source: 'Source/NXDLio/NXDLio.h:865'
      - declaration: 'bool GetFileInfo(String^ strFileName, String^% strDriverName, NCC::XSpatialReference^% sr, int% numLayer, ArrayList^% arrLayerName, ArrayList^% arrGeoName, ArrayList^% arrNumFeature, ArrayList^% arrMinx, ArrayList^% arrMiny, ArrayList^% arrMaxx, ArrayList^% arrMaxy);'
        source: 'Source/NXDLio/NXDLio.h:880'
      - declaration: 'bool GetFileInfo(String^ strFileName, String^% strDriverName, NCC::XSpatialReference^% sr, int% numLayer, ArrayList^% arrLayerName, ArrayList^% arrGeoName, ArrayList^% arrNumFeature, ArrayList^% arrMinx, ArrayList^% arrMiny, ArrayList^% arrMaxx, ArrayList^% arrMaxy, XThread^ thd);'
        source: 'Source/NXDLio/NXDLio.h:896'
  - symbol: XVectorIO.LoadFile
    declaration_candidates:
      - declaration: 'NVC::XvcBase^		LoadFile(String^ strFileName, [OutAttribute] String^% strError, NCC::XSpatialReference^% pInSR);'
        source: 'Source/NXDLio/NXDLio.h:824'
      - declaration: 'NVC::XvcBase^		LoadFile(String^ strFileName, [OutAttribute] String^% strError, NCC::XSpatialReference^% pInSR, [OutAttribute] bool% bExistAttr, bool bLoadProperty);'
        source: 'Source/NXDLio/NXDLio.h:834'
      - declaration: 'NVC::XvcBase^ LoadFile(String^ strFileName, [OutAttribute] String^% strError, NCC::XSpatialReference^% pInSR, XThread^ thd);'
        source: 'Source/NXDLio/NXDLio.h:842'
  - symbol: NXImageView.AddImageLayer
    declaration: 'bool		AddImageLayer(NXImageLayer^% layer);'
    source: 'Source/NXImage/NXImageView.h:836'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
