---
title: Video Image Layer Workflow
aliases:
  - Video Image Layer Workflow
  - wf-video-image-layer
  - wf video image layer
symbols:
  - NXImageLayerVideo
  - XFramePicture
  - XVideoChannel
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Use NXImageLayerVideo when video must live inside an image-view layer stack.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXImageLayerVideo.SetVideoFrame`
  - `NXImageLayerVideo.SetVideoChannel`
  - `NXImageLayerVideo.ResetVideoChannel`
  - `NXImageLayerVideo.SetInitialFrameSize`
  - `NXImageLayerVideo.ImageToWorld`
  - `NXImageLayerVideo.WorldToImage`
  - `NXImageLayerVideo.WorldToSpace`
  - `NXImageLayerVideo.SpaceToWorld`
  - `NXImageLayerVideo.WorldToScreen`
  - `NXImageLayerVideo.ScreenToWorld`
- Verified source:
  - `Source/NXVideo/NXImageLayerVideo.h:57`
  - `Source/NXVideo/NXImageLayerVideo.h:61`
  - `Source/NXVideo/NXImageLayerVideo.h:64`
  - `Source/NXVideo/NXImageLayerVideo.h:71`
  - `Source/NXVideo/NXImageLayerVideo.h:97`
  - `Source/NXVideo/NXImageLayerVideo.h:103`
  - `Source/NXVideo/NXImageLayerVideo.h:111`
  - `Source/NXVideo/NXImageLayerVideo.h:144`
  - `Source/NXVideo/NXImageLayerVideo.h:199`
  - `Source/NXVideo/NXImageLayerVideo.h:205`
- Steps:
  - NXImageView에 레이어를 붙인다.
  - frame 또는 channel을 연결한다.
  - 필요한 Image/World/Space 변환 메서드를 호출한다.

## Required Facts
```yaml
workflow_family: video_view
output_shape: view_shell_or_hosted_control
required_symbols:
  - NXImageLayerVideo.SetVideoFrame
  - NXImageLayerVideo.SetVideoChannel
  - NXImageLayerVideo.ResetVideoChannel
  - NXImageLayerVideo.SetInitialFrameSize
  - NXImageLayerVideo.ImageToWorld
  - NXImageLayerVideo.WorldToImage
  - NXImageLayerVideo.WorldToSpace
  - NXImageLayerVideo.SpaceToWorld
  - NXImageLayerVideo.WorldToScreen
  - NXImageLayerVideo.ScreenToWorld
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
