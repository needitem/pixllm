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
output_shape: hosted_wpf_shell_by_default
required_output_files:
  - MainWindow.xaml
  - MainWindow.xaml.cs
  - App.xaml
  - App.xaml.cs
required_symbols:
  - XVideoIO.OpenFile
  - NXVideoView.SetVideoChannel
  - NXVideoView.ResetVideoChannel
  - NXVideoView.RefreshScreen
  - NXVideoView.RequestRender
  - NXVideoView.AddRenderLayer
  - NXVideoView.CaptureFrame
required_facts:
  - symbol: XVideoIO.OpenFile
    declaration_candidates:
      - declaration: 'NXVideo::XVideo^ OpenFile(String^ strFilePath, String^ strDriverName, [OutAttribute] String^% strError);'
        source: 'Source/NXVideo/XVideoIO.h:432'
      - declaration: 'NXVideo::XVideo^ OpenFile(String^ strFilePath, String^ strDriverName, bool scanWholeFile, bool decodeFrames, XThread^ thread, [OutAttribute] String^% strError);'
        source: 'Source/NXVideo/XVideoIO.h:443'
  - symbol: NXVideoView.SetVideoChannel
    declaration_candidates:
      - declaration: 'bool		SetVideoChannel(XVideo^ video, int channelIndex);'
        source: 'Source/NXVideo/NXVideoView.h:351'
      - declaration: 'bool		SetVideoChannel(XVideoChannel^ channel);'
        source: 'Source/NXVideo/NXVideoView.h:356'
  - symbol: NXVideoView.ResetVideoChannel
    declaration: 'void		ResetVideoChannel();'
    source: 'Source/NXVideo/NXVideoView.h:359'
  - symbol: NXVideoView.RefreshScreen
    declaration: 'bool		RefreshScreen();'
    source: 'Source/NXVideo/NXVideoView.h:193'
  - symbol: NXVideoView.RequestRender
    declaration: 'void		RequestRender(UInt64 requestID);'
    source: 'Source/NXVideo/NXVideoView.h:198'
  - symbol: NXVideoView.AddRenderLayer
    declaration_candidates:
      - declaration: 'bool		AddRenderLayer(NXVideoLayer^ layer);'
        source: 'Source/NXVideo/NXVideoView.h:218'
      - declaration: 'bool		AddRenderLayer(NXVideoLayer^ layer, bool initializing);'
        source: 'Source/NXVideo/NXVideoView.h:224'
  - symbol: NXVideoView.CaptureFrame
    declaration: 'cli::array<XTexture^>^ CaptureFrame(bool bPrimaryOnly);'
    source: 'Source/NXVideo/NXVideoView.h:381'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
