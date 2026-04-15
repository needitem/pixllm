---
title: Video KLV Workflow
aliases:
  - Video KLV Workflow
  - wf-video-klv
  - wf video klv
symbols:
  - NXMpegTSAnalysis
  - XKLVManager
  - XFrameMetad
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Extract KLV metadata from MPEG-TS and decode it through engine helpers.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `NXMpegTSAnalysis.GetKLVMetaData`
  - `XKLVManager.ParseKLVData`
  - `XKLVManager.GetKLVCount`
  - `XKLVManager.GetKey`
  - `XKLVManager.GetValue`
  - `XFrameMetad.GetData`
  - `XFrameMetad.SetData`
  - `XFrameMetad.Decode`
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`
- Steps:
  - TS 패킷에서 KLV를 추출한다.
  - 원시 키/값은 XKLVManager로 파싱한다.
  - typed metadata는 XFrameMetad로 decode한다.

## Required Facts
```yaml
workflow_family: video_view
output_shape: view_shell_or_hosted_control
required_symbols:
  - NXMpegTSAnalysis.GetKLVMetaData
  - XKLVManager.ParseKLVData
  - XKLVManager.GetKLVCount
  - XKLVManager.GetKey
  - XKLVManager.GetValue
  - XFrameMetad.GetData
  - XFrameMetad.SetData
  - XFrameMetad.Decode
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
