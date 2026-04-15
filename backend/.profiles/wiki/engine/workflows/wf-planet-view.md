---
title: Planet View Workflow
aliases:
  - Planet View Workflow
  - wf-planet-view
  - wf planet view
symbols:
  - NXPlanetView
  - NXPlanetLayer
  - NXRenderLayer
  - NXCameraState
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Create NXPlanetView, set camera state, and attach render layers.
- Core calls:
  - `NXPlanetView.SetCameraPosition`
  - `NXPlanetView.SetCameraState`
  - `NXPlanetView.AddRenderLayer`
  - `NXPlanetView.GetDrawArgs`
  - `NXPlanetView.CaptureScreen`
  - `NXPlanetView.SetMouseControlMode`
  - `NXPlanetView.ChangeLayerOrder`
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:103`
  - `Source/NXPlanet/NXPlanetView.h:104`
  - `Source/NXPlanet/NXPlanetView.h:513`
  - `Source/NXPlanet/NXPlanetView.h:516`
  - `Source/NXPlanet/NXPlanetView.h:564`
  - `Source/NXPlanet/NXPlanetView.h:570`
  - `Source/NXPlanet/NXPlanetView.h:536`
  - `Source/NXPlanet/NXPlanetView.h:546`
  - `Source/NXPlanet/NXPlanetView.h:768`
  - `Source/NXPlanet/NXPlanetView.h:804`
  - `Source/NXPlanet/NXPlanetView.h:812`
  - `Source/NXPlanet/NXPlanetView.h:1647`
- Steps:
  - 뷰를 생성한다.
  - 카메라를 설정한다.
  - 렌더 레이어를 추가한다.
  - 필요 시 draw args/capture/mouse control을 사용한다.


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
  - NXPlanetView.SetCameraPosition
  - NXPlanetView.SetCameraState
  - NXPlanetView.AddRenderLayer
  - NXPlanetView.GetDrawArgs
  - NXPlanetView.CaptureScreen
  - NXPlanetView.SetMouseControlMode
  - NXPlanetView.ChangeLayerOrder
required_facts:
  - symbol: NXPlanetView.SetCameraPosition
    declaration_candidates:
      - declaration: 'bool SetCameraPosition(NXDL::XGeoPoint^ pos, NXDL::XAngle^ azimuth);'
        source: 'Source/NXPlanet/NXPlanetView.h:570'
      - declaration: 'bool SetCameraPosition(NXDL::XGeoPoint^ pos, NXDL::XAngle^ yaw, NXDL::XAngle^ pitch, NXDL::XAngle^ roll);'
        source: 'Source/NXPlanet/NXPlanetView.h:578'
      - declaration: 'bool SetCameraPosition(NXDL::XGeoPoint^ pos, NXDL::XAngle^ yaw, NXDL::XAngle^ pitch, NXDL::XAngle^ roll, bool bodyFrame);'
        source: 'Source/NXPlanet/NXPlanetView.h:587'
  - symbol: NXPlanetView.SetCameraState
    declaration: 'bool SetCameraState(NXCameraState^ state);'
    source: 'Source/NXPlanet/NXPlanetView.h:564'
  - symbol: NXPlanetView.AddRenderLayer
    declaration_candidates:
      - declaration: 'bool		AddRenderLayer (NXRenderLayer^% layer);'
        source: 'Source/NXPlanet/NXPlanetView.h:536'
      - declaration: 'bool		AddRenderLayer (NXPlanetLayer^% layer);'
        source: 'Source/NXPlanet/NXPlanetView.h:546'
  - symbol: NXPlanetView.GetDrawArgs
    declaration: 'NXPlanetDrawArgs^ GetDrawArgs();'
    source: 'Source/NXPlanet/NXPlanetView.h:1647'
  - symbol: NXPlanetView.CaptureScreen
    declaration_candidates:
      - declaration: 'Bitmap^	CaptureScreen();'
        source: 'Source/NXPlanet/NXPlanetView.h:812'
      - declaration: 'bool CaptureScreen(String^ outputPath, int nX1, int nX2, int nY1, int nY2, int nOutNX, int nOutNY, NGR::XFrameCaptureBuffer::eCaptureMode mode, [OutAttribute] String^% strErr, XThread^ thd);'
        source: 'Source/NXPlanet/NXPlanetView.h:891'
  - symbol: NXPlanetView.SetMouseControlMode
    declaration: 'void	SetMouseControlMode(DWORD mode);'
    source: 'Source/NXPlanet/NXPlanetView.h:804'
  - symbol: NXPlanetView.ChangeLayerOrder
    declaration: 'bool ChangeLayerOrder(cli::array<NXRenderLayer^>^% layers);'
    source: 'Source/NXPlanet/NXPlanetView.h:768'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
