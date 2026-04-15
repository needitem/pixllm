---
title: Video Playback Workflow
aliases:
  - Video Playback Workflow
  - wf-video-playback
  - wf video playback
symbols:
  - XVideoIO
  - XVideo
  - XVideoChannel
  - NXVideoView
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Open video, choose a channel, and bind it to NXVideoView.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XVideoIO.OpenFile`
  - `NXVideoView.SetVideoChannel`
  - `NXVideoView.ResetVideoChannel`
  - `NXVideoView.RefreshScreen`
  - `NXVideoView.RequestRender`
  - `NXVideoView.AddRenderLayer`
  - `NXVideoView.CaptureFrame`
- Verified source:
  - `Source/NXVideo/XVideoIO.h:432`
  - `Source/NXVideo/XVideoIO.h:443`
  - `Source/NXVideo/NXVideoView.h:129`
  - `Source/NXVideo/NXVideoView.h:144`
  - `Source/NXVideo/NXVideoView.h:193`
  - `Source/NXVideo/NXVideoView.h:198`
  - `Source/NXVideo/NXVideoView.h:202`
  - `Source/NXVideo/NXVideoView.h:218`
  - `Source/NXVideo/NXVideoView.h:351`
  - `Source/NXVideo/NXVideoView.h:356`
  - `Source/NXVideo/NXVideoView.h:359`
  - `Source/NXVideo/NXVideoView.h:381`
- Steps:
  - XVideoIO.OpenFile로 파일을 연다.
  - 채널을 고른다.
  - SetVideoChannel로 뷰와 연결한다.
  - 종료 시 ResetVideoChannel을 호출한다.

## Required Facts
```yaml
workflow_family: video_view
output_shape: view_shell_or_hosted_control
required_symbols:
  - XVideoIO.OpenFile
  - NXVideoView.SetVideoChannel
  - NXVideoView.ResetVideoChannel
  - NXVideoView.RefreshScreen
  - NXVideoView.RequestRender
  - NXVideoView.AddRenderLayer
  - NXVideoView.CaptureFrame
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
