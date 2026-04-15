---
title: Image Composite Manager Workflow
aliases:
  - Image Composite Manager Workflow
  - wf-image-composite-manager
  - wf image composite manager
symbols:
  - NXImageLayerComposites
  - XDMCompManager
  - XDMComposite
  - XDMBand
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Manage composites through NXImageLayerComposites and XDMCompManager.
- Core calls:
  - `NXImageLayerComposites.GetXDMCompManager`
  - `NXImageLayerComposites.Lock`
  - `NXImageLayerComposites.UnLock`
  - `NXImageLayerComposites.EnableCache`
  - `NXImageLayerComposites.EnableThread`
  - `NXImageLayerComposites.SetEnableUpdateAtEnd`
  - `NXImageLayerComposites.InvalidateCache`
  - `NXImageLayerComposites.ReadPixelValues`
  - `NXImageLayerComposites.HitTest`
  - `XDMCompManager.AddXDMComposite`
  - `XDMCompManager.RemoveXDMCompositeAll`
  - `XDMComposite.SetBand`
- Verified source:
  - `Source/NXImage/NXImageLayerComposites.h:142`
  - `Source/NXImage/NXImageLayerComposites.h:149`
  - `Source/NXImage/NXImageLayerComposites.h:153`
  - `Source/NXImage/NXImageLayerComposites.h:157`
  - `Source/NXImage/NXImageLayerComposites.h:164`
  - `Source/NXImage/NXImageLayerComposites.h:168`
  - `Source/NXImage/NXImageLayerComposites.h:176`
  - `Source/NXImage/NXImageLayerComposites.h:196`
  - `Source/NXImage/NXImageLayerComposites.h:313`
  - `Source/NXDLrs/NXDLrs.h:1423`
  - `Source/NXDLrs/NXDLrs.h:1867`
  - `Source/NXDLrs/NXDLrs.h:1880`
- Steps:
  - GetXDMCompManager로 관리자를 얻는다.
  - Lock/UnLock 사이에서 Composite를 갱신한다.
  - 캐시/스레드/inspect API를 필요한 만큼 쓴다.
  - ZoomFit 또는 Invalidate로 반영한다.


## Required Facts
```yaml
workflow_family: image_view
output_shape: hosted_wpf_shell_by_default
required_output_files:
  - MainWindow.xaml
  - MainWindow.xaml.cs
  - App.xaml
  - App.xaml.cs
required_symbols:
  - NXImageLayerComposites.GetXDMCompManager
  - NXImageLayerComposites.Lock
  - NXImageLayerComposites.UnLock
  - NXImageLayerComposites.EnableCache
  - NXImageLayerComposites.EnableThread
  - NXImageLayerComposites.SetEnableUpdateAtEnd
  - NXImageLayerComposites.InvalidateCache
  - NXImageLayerComposites.ReadPixelValues
  - NXImageLayerComposites.HitTest
  - XDMCompManager.AddXDMComposite
  - XDMCompManager.RemoveXDMCompositeAll
  - XDMComposite.SetBand
required_facts:
  - symbol: NXImageLayerComposites.GetXDMCompManager
    declaration: 'XDMCompManager^	GetXDMCompManager();'
    source: 'Source/NXImage/NXImageLayerComposites.h:149'
  - symbol: NXImageLayerComposites.Lock
    declaration: 'bool	Lock();'
    source: 'Source/NXImage/NXImageLayerComposites.h:153'
  - symbol: NXImageLayerComposites.UnLock
    declaration: 'bool	UnLock();'
    source: 'Source/NXImage/NXImageLayerComposites.h:157'
  - symbol: NXImageLayerComposites.EnableCache
    declaration: 'void	EnableCache(bool bEnable);'
    source: 'Source/NXImage/NXImageLayerComposites.h:164'
  - symbol: NXImageLayerComposites.EnableThread
    declaration: 'void	EnableThread(bool bEnable);'
    source: 'Source/NXImage/NXImageLayerComposites.h:168'
  - symbol: NXImageLayerComposites.SetEnableUpdateAtEnd
    declaration: 'void	SetEnableUpdateAtEnd(bool bEnable);'
    source: 'Source/NXImage/NXImageLayerComposites.h:176'
  - symbol: NXImageLayerComposites.InvalidateCache
    declaration: 'void	InvalidateCache();'
    source: 'Source/NXImage/NXImageLayerComposites.h:185'
  - symbol: NXImageLayerComposites.ReadPixelValues
    declaration: 'bool ReadPixelValues(int sx, int sy, bool bFirstHit, double% val01, double% val02, double% val03);'
    source: 'Source/NXImage/NXImageLayerComposites.h:196'
  - symbol: NXImageLayerComposites.HitTest
    declaration: 'bool HitTest(XVertex2d^ vWorld, XDMComposite^% pHitComp);'
    source: 'Source/NXImage/NXImageLayerComposites.h:313'
  - symbol: XDMCompManager.AddXDMComposite
    declaration: 'bool		AddXDMComposite(XDMComposite^% Comp);'
    source: 'Source/NXDLrs/NXDLrs.h:1867'
  - symbol: XDMCompManager.RemoveXDMCompositeAll
    declaration: 'void		RemoveXDMCompositeAll();'
    source: 'Source/NXDLrs/NXDLrs.h:1880'
  - symbol: XDMComposite.SetBand
    declaration_candidates:
      - declaration: 'void		SetBand(XDMBand^% band, int Idx);'
        source: 'Source/NXDLrs/NXDLrs.h:1423'
      - declaration: 'void		SetBand(XDMBand^% band, eCompBandIdx Idx);'
        source: 'Source/NXDLrs/NXDLrs.h:1428'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
