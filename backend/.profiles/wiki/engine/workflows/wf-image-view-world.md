---
title: Image View World Workflow
aliases:
  - Image View World Workflow
  - wf-image-view-world
  - wf image view world
symbols:
  - NXImageView
  - XVertex2d
  - XAngle
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Control zoom and world state on NXImageView.
- Core calls:
  - `NXImageView.ZoomFit`
  - `NXImageView.ZoomOneToOne`
  - `NXImageView.ZoomFitRect`
  - `NXImageView.SetWorld`
  - `NXImageView.SetWorldToCenter`
  - `NXImageView.SetWorldPerScreen`
  - `NXImageView.LinkCameraFrom`
  - `NXImageView.RefreshScreen`
- Verified source:
  - `Source/NXImage/NXImageView.h:198`
  - `Source/NXImage/NXImageView.h:206`
  - `Source/NXImage/NXImageView.h:219`
  - `Source/NXImage/NXImageView.h:224`
  - `Source/NXImage/NXImageView.h:228`
  - `Source/NXImage/NXImageView.h:235`
  - `Source/NXImage/NXImageView.h:241`
  - `Source/NXImage/NXImageView.h:253`
- Steps:
  - fit/zoom/world-set 목적을 먼저 정한다.
  - 해당 NXImageView 메서드를 호출한다.
  - 멀티뷰면 LinkCameraFrom을 쓴다.
  - 필요 시 RefreshScreen으로 반영한다.


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
  - NXImageView.ZoomFit
  - NXImageView.ZoomOneToOne
  - NXImageView.ZoomFitRect
  - NXImageView.SetWorld
  - NXImageView.SetWorldToCenter
  - NXImageView.SetWorldPerScreen
  - NXImageView.LinkCameraFrom
  - NXImageView.RefreshScreen
required_facts:
  - symbol: NXImageView.ZoomFit
    declaration: 'bool	ZoomFit();'
    source: 'Source/NXImage/NXImageView.h:198'
  - symbol: NXImageView.ZoomOneToOne
    declaration: 'bool	ZoomOneToOne();'
    source: 'Source/NXImage/NXImageView.h:206'
  - symbol: NXImageView.ZoomFitRect
    declaration: 'bool	ZoomFitRect(double llx, double lly, double urx, double ury);'
    source: 'Source/NXImage/NXImageView.h:219'
  - symbol: NXImageView.SetWorld
    declaration: 'bool	SetWorld(XVertex2d^ vCenter, XVertex2d^ vPixelSize, XAngle^ aRotate);'
    source: 'Source/NXImage/NXImageView.h:235'
  - symbol: NXImageView.SetWorldToCenter
    declaration: 'bool	SetWorldToCenter(double wcx, double wcy);'
    source: 'Source/NXImage/NXImageView.h:241'
  - symbol: NXImageView.SetWorldPerScreen
    declaration: 'bool	SetWorldPerScreen(double wpx, double wpy);'
    source: 'Source/NXImage/NXImageView.h:253'
  - symbol: NXImageView.LinkCameraFrom
    declaration: 'bool	LinkCameraFrom(NXImageView^ view);'
    source: 'Source/NXImage/NXImageView.h:224'
  - symbol: NXImageView.RefreshScreen
    declaration: 'bool	RefreshScreen();'
    source: 'Source/NXImage/NXImageView.h:228'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
