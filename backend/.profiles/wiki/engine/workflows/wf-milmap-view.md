---
title: Milmap View Workflow
aliases:
  - Milmap View Workflow
  - wf-milmap-view
  - wf milmap view
symbols:
  - NXMilmapView
  - NXMilmapLayer
  - NXRenderLayer
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Control scale, center, layers, draw args, and capture on NXMilmapView.
- Core calls:
  - `NXMilmapView.CheckMilmapData`
  - `NXMilmapView.SetGeoToCenter`
  - `NXMilmapView.SearchScale`
  - `NXMilmapView.Zoom`
  - `NXMilmapView.ZoomFitRect`
  - `NXMilmapView.IsExistScale`
  - `NXMilmapView.SearchName`
  - `NXMilmapView.ShowCross`
  - `NXMilmapView.RefreshScreen`
  - `NXMilmapView.AddRenderLayer`
  - `NXMilmapView.ChangeLayerOrder`
  - `NXMilmapView.GetDrawArgs`
  - `NXMilmapView.CaptureScreen`
- Verified source:
  - `Source/NXMilmap/NXMilmapView.h:110`
  - `Source/NXMilmap/NXMilmapView.h:116`
  - `Source/NXMilmap/NXMilmapView.h:125`
  - `Source/NXMilmap/NXMilmapView.h:131`
  - `Source/NXMilmap/NXMilmapView.h:141`
  - `Source/NXMilmap/NXMilmapView.h:146`
  - `Source/NXMilmap/NXMilmapView.h:151`
  - `Source/NXMilmap/NXMilmapView.h:155`
  - `Source/NXMilmap/NXMilmapView.h:159`
  - `Source/NXMilmap/NXMilmapView.h:165`
  - `Source/NXMilmap/NXMilmapView.h:220`
  - `Source/NXMilmap/NXMilmapView.h:231`
  - `Source/NXMilmap/NXMilmapView.h:242`
- Steps:
  - 데이터/축척 가능 여부를 확인한다.
  - SetGeoToCenter나 Zoom 계열로 위치를 맞춘다.
  - 레이어를 붙이고 필요 시 순서를 바꾼다.
  - draw args/capture/crosshair를 쓴다.


## Required Facts
```yaml
workflow_family: map_view
output_shape: hosted_wpf_shell_by_default
required_output_files:
  - MainWindow.xaml
  - MainWindow.xaml.cs
  - App.xaml
  - App.xaml.cs
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
    declaration: 'bool	CheckMilmapData(XVertex2d^ vGeo, int nScaleIndex);'
    source: 'Source/NXMilmap/NXMilmapView.h:110'
  - symbol: NXMilmapView.SetGeoToCenter
    declaration: 'bool	SetGeoToCenter(int nScaleIndex, XVertex2d^ vGeo);'
    source: 'Source/NXMilmap/NXMilmapView.h:116'
  - symbol: NXMilmapView.SearchScale
    declaration: 'int		SearchScale(String^ m);'
    source: 'Source/NXMilmap/NXMilmapView.h:125'
  - symbol: NXMilmapView.Zoom
    declaration: 'bool	Zoom(int scaleIndex, double factor);'
    source: 'Source/NXMilmap/NXMilmapView.h:131'
  - symbol: NXMilmapView.ZoomFitRect
    declaration: 'bool	ZoomFitRect(int scaleIndex, double llx, double lly, double urx, double ury, bool bAuto);'
    source: 'Source/NXMilmap/NXMilmapView.h:141'
  - symbol: NXMilmapView.IsExistScale
    declaration: 'bool	IsExistScale(int index);'
    source: 'Source/NXMilmap/NXMilmapView.h:146'
  - symbol: NXMilmapView.SearchName
    declaration: 'String^	SearchName(int index);'
    source: 'Source/NXMilmap/NXMilmapView.h:151'
  - symbol: NXMilmapView.ShowCross
    declaration: 'void	ShowCross(bool bShow);'
    source: 'Source/NXMilmap/NXMilmapView.h:155'
  - symbol: NXMilmapView.RefreshScreen
    declaration: 'bool	RefreshScreen();'
    source: 'Source/NXMilmap/NXMilmapView.h:159'
  - symbol: NXMilmapView.AddRenderLayer
    declaration_candidates:
      - declaration: 'bool	AddRenderLayer(NXMilmapLayer^% layer);'
        source: 'Source/NXMilmap/NXMilmapView.h:165'
      - declaration: 'bool	AddRenderLayer(NXRenderLayer^% layer);'
        source: 'Source/NXMilmap/NXMilmapView.h:220'
  - symbol: NXMilmapView.ChangeLayerOrder
    declaration: 'bool		ChangeLayerOrder(cli::array<NXRenderLayer^>^% layers);'
    source: 'Source/NXMilmap/NXMilmapView.h:231'
  - symbol: NXMilmapView.GetDrawArgs
    declaration: 'NXMilmapDrawArgs^	GetDrawArgs();'
    source: 'Source/NXMilmap/NXMilmapView.h:242'
  - symbol: NXMilmapView.CaptureScreen
    declaration_candidates:
      - declaration: 'Bitmap^	CaptureScreen();'
        source: 'Source/NXMilmap/NXMilmapView.h:120'
      - declaration: 'Bitmap^	CaptureScreen(int left, int top, int width, int height, bool bOnlyComposite);'
        source: 'Source/NXMilmap/NXMilmapView.h:426'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
