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
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
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
output_shape: view_shell_or_hosted_control
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
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```

## Output Guidance
- Explanation requests: summarize file/channel binding, playback or filter state changes, and refresh/render calls.
- Code/sample requests: include the host/view shell plus the ordered playback or layer-binding path.
- If the user asks for WPF, include the XAML shell and code-behind instead of returning only a single `.cs` file.

## Common Wrong Patterns
- Do not invent helper methods or short overloads outside the verified symbol set above.
- Do not convert verified methods into properties, or properties into methods, without source proof.
- Do not guess `ref`/`out`, enum literals, or return types from naming alone.
- Do not skip prerequisites implied by the ordered call chain in this workflow.
- Do not collapse playback, channel binding, and refresh/render control into a single guessed helper call.

- See also:
  - [xdl-videoview-wpf-examples.md](xdl-videoview-wpf-examples.md)
