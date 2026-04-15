---
title: Raster Load Workflow
aliases:
  - Raster Load Workflow
  - wf-raster-load
  - wf raster load
symbols:
  - XRasterIO
  - XVectorIO
  - XRawDataParam
  - XRSLoadFile
  - XvcBase
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Initialize XRasterIO/XVectorIO and load data.
- Core calls:
  - `XRasterIO.Initialize`
  - `XRasterIO.LoadFile`
  - `XRasterIO.GetSubDatasets`
  - `XRasterIO.LoadRawFile`
  - `XRasterIO.GetFileInfo`
  - `XVectorIO.Initialize`
  - `XVectorIO.LoadFile`
  - `XVectorIO.GetFileInfo`
- Verified source:
  - `Source/NXDLio/NXDLio.h:198`
  - `Source/NXDLio/NXDLio.h:230`
  - `Source/NXDLio/NXDLio.h:285`
  - `Source/NXDLio/NXDLio.h:340`
  - `Source/NXDLio/NXDLio.h:557`
  - `Source/NXDLio/NXDLio.h:568`
  - `Source/NXDLio/NXDLio.h:802`
  - `Source/NXDLio/NXDLio.h:824`
  - `Source/NXDLio/NXDLio.h:865`
- Steps:
  - IO 매니저를 생성하고 Initialize를 호출한다.
  - LoadFile 또는 LoadRawFile 경로를 고른다.
  - 멀티서브데이터셋이면 GetSubDatasets를 먼저 본다.
  - 벡터면 XVectorIO 경로로 분기한다.


## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XRasterIO.Initialize
  - XRasterIO.LoadFile
  - XRasterIO.GetSubDatasets
  - XRasterIO.LoadRawFile
  - XRasterIO.GetFileInfo
  - XVectorIO.Initialize
  - XVectorIO.LoadFile
  - XVectorIO.GetFileInfo
required_facts:
  - symbol: XRasterIO.Initialize
    declaration: 'bool		Initialize([OutAttribute] String^% strError);'
    source: 'Source/NXDLio/NXDLio.h:198'
  - symbol: XRasterIO.LoadFile
    declaration_candidates:
      - declaration: 'NRS::XRSLoadFile^	LoadFile(String^ strFileKey, String^ strFileName, [OutAttribute] String^% strError, bool bCalcStatistics , eIOCreateXLDMode CreateXLD);'
        source: 'Source/NXDLio/NXDLio.h:222'
      - declaration: 'NRS::XRSLoadFile^	LoadFile(String^ strFileName, [OutAttribute] String^% strError, bool bCalcStatistics, eIOCreateXLDMode CreateXLD);'
        source: 'Source/NXDLio/NXDLio.h:230'
      - declaration: 'NRS::XRSLoadFile^	LoadFile(String^ strFileKey, String^ strFileName, [OutAttribute] String^% strError, bool bCalcStatistics , eIOCreateXLDMode CreateXLD, bool bMetaLoad);'
        source: 'Source/NXDLio/NXDLio.h:240'
  - symbol: XRasterIO.GetSubDatasets
    declaration: 'cli::array<String^>^ GetSubDatasets(String^ strFileName);'
    source: 'Source/NXDLio/NXDLio.h:340'
  - symbol: XRasterIO.LoadRawFile
    declaration: 'NRS::XRSLoadFile^ LoadRawFile(String^ strFileName, XRawDataParam^ param, [OutAttribute] String^% strError, bool bCalcStatistics, eIOCreateXLDMode CreateXLD);'
    source: 'Source/NXDLio/NXDLio.h:557'
  - symbol: XRasterIO.GetFileInfo
    declaration_candidates:
      - declaration: 'String^ GetFileInfo(String^ strFileName, [OutAttribute] String^% strError);'
        source: 'Source/NXDLio/NXDLio.h:568'
      - declaration: 'String^ GetFileInfo(String^ strFileName, int nSubIdx, [OutAttribute] String^% strError);'
        source: 'Source/NXDLio/NXDLio.h:575'
  - symbol: XVectorIO.Initialize
    declaration: 'bool		Initialize([OutAttribute] String^% strError);'
    source: 'Source/NXDLio/NXDLio.h:802'
  - symbol: XVectorIO.LoadFile
    declaration_candidates:
      - declaration: 'NVC::XvcBase^		LoadFile(String^ strFileName, [OutAttribute] String^% strError, NCC::XSpatialReference^% pInSR);'
        source: 'Source/NXDLio/NXDLio.h:824'
      - declaration: 'NVC::XvcBase^		LoadFile(String^ strFileName, [OutAttribute] String^% strError, NCC::XSpatialReference^% pInSR, [OutAttribute] bool% bExistAttr, bool bLoadProperty);'
        source: 'Source/NXDLio/NXDLio.h:834'
      - declaration: 'NVC::XvcBase^ LoadFile(String^ strFileName, [OutAttribute] String^% strError, NCC::XSpatialReference^% pInSR, XThread^ thd);'
        source: 'Source/NXDLio/NXDLio.h:842'
  - symbol: XVectorIO.GetFileInfo
    declaration_candidates:
      - declaration: 'bool GetFileInfo(String^ strFileName, double% minx, double% miny, double% minz, double% maxx, double% maxy, double% maxz, NCC::XSpatialReference^% sr);'
        source: 'Source/NXDLio/NXDLio.h:865'
      - declaration: 'bool GetFileInfo(String^ strFileName, String^% strDriverName, NCC::XSpatialReference^% sr, int% numLayer, ArrayList^% arrLayerName, ArrayList^% arrGeoName, ArrayList^% arrNumFeature, ArrayList^% arrMinx, ArrayList^% arrMiny, ArrayList^% arrMaxx, ArrayList^% arrMaxy);'
        source: 'Source/NXDLio/NXDLio.h:880'
      - declaration: 'bool GetFileInfo(String^ strFileName, String^% strDriverName, NCC::XSpatialReference^% sr, int% numLayer, ArrayList^% arrLayerName, ArrayList^% arrGeoName, ArrayList^% arrNumFeature, ArrayList^% arrMinx, ArrayList^% arrMiny, ArrayList^% arrMaxx, ArrayList^% arrMaxy, XThread^ thd);'
        source: 'Source/NXDLio/NXDLio.h:896'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
