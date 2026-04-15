---
title: Raster Composite Workflow
aliases:
  - Raster Composite Workflow
  - wf-raster-composite
  - wf raster composite
symbols:
  - XRSLoadFile
  - XDMBand
  - XDMComposite
  - XDMCompManager
  - NXImageLayerComposites
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Build grayscale or RGB composites from raster bands.
- Core calls:
  - `XRSLoadFile.GetBandAt`
  - `XDMComposite.SetBand`
  - `XDMCompManager.AddXDMComposite`
  - `XDMCompManager.RemoveXDMCompositeAll`
  - `NXImageLayerComposites.GetXDMCompManager`
  - `NXImageLayerComposites.ZoomFit`
- Verified source:
  - `Source/NXDLio/NXDLio.h:103`
  - `Source/NXDLio/NXDLio.h:104`
  - `Source/NXDLrs/NXDLrs.h:1370`
  - `Source/NXDLrs/NXDLrs.h:1376`
  - `Source/NXDLrs/NXDLrs.h:1377`
  - `Source/NXDLrs/NXDLrs.h:1378`
  - `Source/NXDLrs/NXDLrs.h:1387`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:142`
- Steps:
  - 파일에서 밴드 수를 확인한다.
  - 그레이면 1밴드, 컬러면 3밴드를 SetBand로 연결한다.
  - 관리자에 등록하고 ZoomFit으로 맞춘다.


## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XRSLoadFile.GetBandAt
  - XDMComposite.SetBand
  - XDMCompManager.AddXDMComposite
  - XDMCompManager.RemoveXDMCompositeAll
  - NXImageLayerComposites.GetXDMCompManager
  - NXImageLayerComposites.ZoomFit
required_facts:
  - symbol: XRSLoadFile.GetBandAt
    declaration: 'XDMBand^	GetBandAt(int nIndex);'
    source: 'Source/NXDLrs/XRSFile.h:986'
  - symbol: XDMComposite.SetBand
    declaration_candidates:
      - declaration: 'void		SetBand(XDMBand^% band, int Idx);'
        source: 'Source/NXDLrs/NXDLrs.h:1423'
      - declaration: 'void		SetBand(XDMBand^% band, eCompBandIdx Idx);'
        source: 'Source/NXDLrs/NXDLrs.h:1428'
  - symbol: XDMCompManager.AddXDMComposite
    declaration: 'bool		AddXDMComposite(XDMComposite^% Comp);'
    source: 'Source/NXDLrs/NXDLrs.h:1867'
  - symbol: XDMCompManager.RemoveXDMCompositeAll
    declaration: 'void		RemoveXDMCompositeAll();'
    source: 'Source/NXDLrs/NXDLrs.h:1880'
  - symbol: NXImageLayerComposites.GetXDMCompManager
    declaration: 'XDMCompManager^	GetXDMCompManager();'
    source: 'Source/NXImage/NXImageLayerComposites.h:149'
  - symbol: NXImageLayerComposites.ZoomFit
    declaration: 'bool	ZoomFit();'
    source: 'Source/NXImage/NXImageLayerComposites.h:142'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
