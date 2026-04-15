---
title: Uspace View Workflow
aliases:
  - Uspace View Workflow
  - wf-uspace-view
  - wf uspace view
symbols:
  - NXUspaceView
  - NXRenderLayer
  - NXCameraState
  - XVertex3d
  - XSpatialReference
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Define region, camera, SR, and interaction mode on NXUspaceView.
- Core calls:
  - `NXUspaceView.AddRenderLayer`
  - `NXUspaceView.SetSpaceRegion`
  - `NXUspaceView.SetCameraState`
  - `NXUspaceView.RefreshScreen`
  - `NXUspaceView.SetSR`
  - `NXUspaceView.GetSR`
  - `NXUspaceView.SpaceToWorld`
  - `NXUspaceView.SpaceToScreen`
  - `NXUspaceView.GetDrawArgs`
  - `NXUspaceView.SetMouseControlMode`
  - `NXUspaceView.GetMouseControlMode`
- Verified source:
  - `Source/NXUspace/NXUspaceView.h:87`
  - `Source/NXUspace/NXUspaceView.h:93`
  - `Source/NXUspace/NXUspaceView.h:99`
  - `Source/NXUspace/NXUspaceView.h:106`
  - `Source/NXUspace/NXUspaceView.h:110`
  - `Source/NXUspace/NXUspaceView.h:114`
  - `Source/NXUspace/NXUspaceView.h:117`
  - `Source/NXUspace/NXUspaceView.h:120`
  - `Source/NXUspace/NXUspaceView.h:124`
  - `Source/NXUspace/NXUspaceView.h:128`
  - `Source/NXUspace/NXUspaceView.h:132`
- Steps:
  - 공간 범위와 카메라를 먼저 정한다.
  - SR과 레이어를 설정한다.
  - 필요 시 world/screen 변환과 mouse control을 사용한다.


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
  - NXUspaceView.AddRenderLayer
  - NXUspaceView.SetSpaceRegion
  - NXUspaceView.SetCameraState
  - NXUspaceView.RefreshScreen
  - NXUspaceView.SetSR
  - NXUspaceView.GetSR
  - NXUspaceView.SpaceToWorld
  - NXUspaceView.SpaceToScreen
  - NXUspaceView.GetDrawArgs
  - NXUspaceView.SetMouseControlMode
  - NXUspaceView.GetMouseControlMode
required_facts:
  - symbol: NXUspaceView.AddRenderLayer
    declaration: 'bool	AddRenderLayer (NXRenderLayer^% layer);'
    source: 'Source/NXUspace/NXUspaceView.h:87'
  - symbol: NXUspaceView.SetSpaceRegion
    declaration: 'void	SetSpaceRegion(XVertex2d^ vMinSpace, XVertex2d^ vMaxSpace, XVertex2d^ vPsz);'
    source: 'Source/NXUspace/NXUspaceView.h:93'
  - symbol: NXUspaceView.SetCameraState
    declaration: 'void	SetCameraState(XVertex3d^ vEye, XVertex3d^ vLookAt, XVertex3d^ vUp);'
    source: 'Source/NXUspace/NXUspaceView.h:99'
  - symbol: NXUspaceView.RefreshScreen
    declaration: 'void	RefreshScreen();'
    source: 'Source/NXUspace/NXUspaceView.h:106'
  - symbol: NXUspaceView.SetSR
    declaration: 'void	SetSR(NCC::XSpatialReference^ sr);'
    source: 'Source/NXUspace/NXUspaceView.h:110'
  - symbol: NXUspaceView.GetSR
    declaration: 'NCC::XSpatialReference^ GetSR();'
    source: 'Source/NXUspace/NXUspaceView.h:114'
  - symbol: NXUspaceView.SpaceToWorld
    declaration: 'NXDL::XVertex3d^ SpaceToWorld(NXDL::XVertex3d^ vSpace);'
    source: 'Source/NXUspace/NXUspaceView.h:117'
  - symbol: NXUspaceView.SpaceToScreen
    declaration: 'NXDL::XVertex3d^ SpaceToScreen(NXDL::XVertex3d^ vSpace);'
    source: 'Source/NXUspace/NXUspaceView.h:120'
  - symbol: NXUspaceView.GetDrawArgs
    declaration: 'NXDL::NXUSpace::NXUspaceDrawArgs^	GetDrawArgs();'
    source: 'Source/NXUspace/NXUspaceView.h:124'
  - symbol: NXUspaceView.SetMouseControlMode
    declaration: 'void	SetMouseControlMode(DWORD mode);'
    source: 'Source/NXUspace/NXUspaceView.h:128'
  - symbol: NXUspaceView.GetMouseControlMode
    declaration: 'DWORD	GetMouseControlMode();'
    source: 'Source/NXUspace/NXUspaceView.h:132'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
