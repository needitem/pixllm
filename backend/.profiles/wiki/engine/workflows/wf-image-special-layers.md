---
title: Image Special Layers Workflow
aliases:
  - Image Special Layers Workflow
  - wf-image-special-layers
  - wf image special layers
symbols:
  - NXImageLayerCompLink
  - NXImageLayerStereoComposites
  - NXImageView
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Use comparison and stereo image layers.
- Core calls:
  - `NXImageLayerCompLink.ZoomFit`
  - `NXImageLayerStereoComposites.GetXDMCompManagerL`
  - `NXImageLayerStereoComposites.GetXDMCompManagerR`
  - `NXImageLayerStereoComposites.ZoomFit`
  - `NXImageView.StereoViewType`
  - `NXImageView.StereoColorMaskL`
  - `NXImageView.StereoColorMaskR`
- Verified source:
  - `Source/NXImage/NXImageLayerCompLink.h:151`
  - `Source/NXImage/NXImageLayerCompLink.h:192`
  - `Source/NXImage/NXImageLayerStereoComposites.h:54`
  - `Source/NXImage/NXImageLayerStereoComposites.h:69`
  - `Source/NXImage/NXImageLayerStereoComposites.h:77`
  - `Source/NXImage/NXImageLayerStereoComposites.h:146`
  - `Source/NXImage/NXImageLayerStereoComposites.h:150`
  - `Source/NXImage/NXImageLayerStereoComposites.h:218`
- Steps:
  - 특수 레이어를 일반 이미지 레이어처럼 붙인다.
  - comp-link 또는 stereo 전용 설정을 적용한다.
  - 좌우 manager와 view stereo 속성을 맞춘다.


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
  - NXImageLayerCompLink.ZoomFit
  - NXImageLayerStereoComposites.GetXDMCompManagerL
  - NXImageLayerStereoComposites.GetXDMCompManagerR
  - NXImageLayerStereoComposites.ZoomFit
  - NXImageView.StereoViewType
  - NXImageView.StereoColorMaskL
  - NXImageView.StereoColorMaskR
required_facts:
  - symbol: NXImageLayerCompLink.ZoomFit
    declaration: 'bool			ZoomFit();'
    source: 'Source/NXImage/NXImageLayerCompLink.h:192'
  - symbol: NXImageLayerStereoComposites.GetXDMCompManagerL
    declaration: 'NRS::XDMCompManager^ GetXDMCompManagerL();'
    source: 'Source/NXImage/NXImageLayerStereoComposites.h:146'
  - symbol: NXImageLayerStereoComposites.GetXDMCompManagerR
    declaration: 'NRS::XDMCompManager^ GetXDMCompManagerR();'
    source: 'Source/NXImage/NXImageLayerStereoComposites.h:150'
  - symbol: NXImageLayerStereoComposites.ZoomFit
    declaration: 'bool		ZoomFit();'
    source: 'Source/NXImage/NXImageLayerStereoComposites.h:218'
  - symbol: NXImageView.StereoViewType
    declaration: 'property eStereoType StereoViewType { eStereoType get(); void set(eStereoType val); }'
    source: 'Source/NXImage/NXImageView.h:135'
  - symbol: NXImageView.StereoColorMaskL
    declaration: 'property eStereoColorMask StereoColorMaskL { eStereoColorMask get(); void set(eStereoColorMask val); }'
    source: 'Source/NXImage/NXImageView.h:147'
  - symbol: NXImageView.StereoColorMaskR
    declaration: 'property eStereoColorMask StereoColorMaskR { eStereoColorMask get(); void set(eStereoColorMask val); }'
    source: 'Source/NXImage/NXImageView.h:150'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
