---
title: Video Filter Workflow
aliases:
  - Video Filter Workflow
  - wf-video-filter
  - wf video filter
symbols:
  - NXImageLayerVideo
  - NXVideoView
  - eVideoFilterType
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Adjust brightness, contrast, saturation, gamma, HDR, sharpen, and filter type through video properties.
- Core calls:
  - `NXImageLayerVideo.VideoBrightness`
  - `NXImageLayerVideo.VideoContrast`
  - `NXImageLayerVideo.VideoSaturation`
  - `NXImageLayerVideo.VideoGammaFactor`
  - `NXImageLayerVideo.VideoHDR`
  - `NXImageLayerVideo.VideoSharpenSigma`
  - `NXImageLayerVideo.VideoFilterType`
  - `NXImageLayerVideo.VideoFilterSize`
  - `NXVideoView.FilterType`
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:209`
  - `Source/NXVideo/NXImageLayerVideo.h:211`
  - `Source/NXVideo/NXImageLayerVideo.h:213`
  - `Source/NXVideo/NXImageLayerVideo.h:216`
  - `Source/NXVideo/NXImageLayerVideo.h:219`
  - `Source/NXVideo/NXImageLayerVideo.h:222`
  - `Source/NXVideo/NXImageLayerVideo.h:225`
  - `Source/NXVideo/NXImageLayerVideo.h:227`
  - `Source/NXVideo/NXVideoView.h:38`
  - `Source/NXVideo/NXVideoView.h:413`
- Steps:
  - 비디오를 먼저 바인딩한다.
  - 화질 파라미터를 한 축씩 조정한다.
  - 필터 타입과 사이즈를 맞춘다.


## Required Facts
```yaml
workflow_family: video_view
output_shape: hosted_wpf_shell_by_default
required_output_files:
  - MainWindow.xaml
  - MainWindow.xaml.cs
  - App.xaml
  - App.xaml.cs
required_symbols:
  - NXImageLayerVideo.VideoBrightness
  - NXImageLayerVideo.VideoContrast
  - NXImageLayerVideo.VideoSaturation
  - NXImageLayerVideo.VideoGammaFactor
  - NXImageLayerVideo.VideoHDR
  - NXImageLayerVideo.VideoSharpenSigma
  - NXImageLayerVideo.VideoFilterType
  - NXImageLayerVideo.VideoFilterSize
  - NXVideoView.FilterType
required_facts:
  - symbol: NXImageLayerVideo.VideoBrightness
    declaration: 'property float		VideoBrightness {float get(); void set(float val); }'
    source: 'Source/NXVideo/NXImageLayerVideo.h:209'
  - symbol: NXImageLayerVideo.VideoContrast
    declaration: 'property float		VideoContrast {float get(); void set(float val); }'
    source: 'Source/NXVideo/NXImageLayerVideo.h:213'
  - symbol: NXImageLayerVideo.VideoSaturation
    declaration: 'property float		VideoSaturation {float get(); void set(float val); }'
    source: 'Source/NXVideo/NXImageLayerVideo.h:211'
  - symbol: NXImageLayerVideo.VideoGammaFactor
    declaration: 'property float		VideoGammaFactor {float get(); void set(float val); }'
    source: 'Source/NXVideo/NXImageLayerVideo.h:216'
  - symbol: NXImageLayerVideo.VideoHDR
    declaration: 'property bool		VideoHDR {bool get(); void set(bool val); }'
    source: 'Source/NXVideo/NXImageLayerVideo.h:219'
  - symbol: NXImageLayerVideo.VideoSharpenSigma
    declaration: 'property float		VideoSharpenSigma {float get(); void set(float val); }'
    source: 'Source/NXVideo/NXImageLayerVideo.h:222'
  - symbol: NXImageLayerVideo.VideoFilterType
    declaration: 'property eVideoFilterType VideoFilterType { void set(eVideoFilterType val); }'
    source: 'Source/NXVideo/NXImageLayerVideo.h:225'
  - symbol: NXImageLayerVideo.VideoFilterSize
    declaration: 'property int		VideoFilterSize {int get(); void set(int val); }'
    source: 'Source/NXVideo/NXImageLayerVideo.h:227'
  - symbol: NXVideoView.FilterType
    declaration: 'property eVideoFilterType FilterType { void set(eVideoFilterType val); }'
    source: 'Source/NXVideo/NXVideoView.h:413'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
