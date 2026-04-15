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
output_shape: hosted_wpf_shell_by_default
required_output_files:
  - MainWindow.xaml
  - MainWindow.xaml.cs
  - App.xaml
  - App.xaml.cs
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
required_facts:
  - symbol: NXImageLayerVideo.SetVideoFrame
    declaration: 'void SetVideoFrame(XFramePicture^ frame);'
    source: 'Source/NXVideo/NXImageLayerVideo.h:57'
  - symbol: NXImageLayerVideo.SetVideoChannel
    declaration: 'void SetVideoChannel(XVideoChannel^ channel);'
    source: 'Source/NXVideo/NXImageLayerVideo.h:61'
  - symbol: NXImageLayerVideo.ResetVideoChannel
    declaration: 'void ResetVideoChannel();'
    source: 'Source/NXVideo/NXImageLayerVideo.h:64'
  - symbol: NXImageLayerVideo.SetInitialFrameSize
    declaration: 'void SetInitialFrameSize(int width, int height);'
    source: 'Source/NXVideo/NXImageLayerVideo.h:71'
  - symbol: NXImageLayerVideo.ImageToWorld
    declaration: 'bool		ImageToWorld(XVertex2d^ ptImage, [OutAttribute] XVertex2d^% ptWorld);'
    source: 'Source/NXVideo/NXImageLayerVideo.h:97'
  - symbol: NXImageLayerVideo.WorldToImage
    declaration: 'bool		WorldToImage(XVertex2d^ ptWorld, [OutAttribute] XVertex2d^% ptImage);'
    source: 'Source/NXVideo/NXImageLayerVideo.h:103'
  - symbol: NXImageLayerVideo.WorldToSpace
    declaration_candidates:
      - declaration: 'bool		WorldToSpace(long long nPts, XVertex2d^ ptWorld, [OutAttribute] XVertex3d^% ptSpace);'
        source: 'Source/NXVideo/NXImageLayerVideo.h:111'
      - declaration: 'bool		WorldToSpace(long long nPts, XVertex2d^ ptWorld, double height, [OutAttribute] XVertex3d^% ptSpace);'
        source: 'Source/NXVideo/NXImageLayerVideo.h:120'
      - declaration: 'bool		WorldToSpace(long long nPts, XVertex2d^ ptWorld, [OutAttribute] XGeoPoint^% ptSpace);'
        source: 'Source/NXVideo/NXImageLayerVideo.h:128'
  - symbol: NXImageLayerVideo.SpaceToWorld
    declaration_candidates:
      - declaration: 'bool		SpaceToWorld(long long nPts, XVertex3d^ ptSpace, [OutAttribute] XVertex2d^% ptWorld);'
        source: 'Source/NXVideo/NXImageLayerVideo.h:144'
      - declaration: 'bool		SpaceToWorld(long long nPts, XGeoPoint^ ptSpace, [OutAttribute] XVertex2d^% ptWorld);'
        source: 'Source/NXVideo/NXImageLayerVideo.h:151'
      - declaration: 'bool		SpaceToWorld(XVertex3d^ ptSpace, [OutAttribute] XVertex2d^% ptWorld);'
        source: 'Source/NXVideo/NXImageLayerVideo.h:187'
  - symbol: NXImageLayerVideo.WorldToScreen
    declaration: 'bool		WorldToScreen(XVertex2d^ ptWorld, [OutAttribute] XVertex2d^% ptScreen);'
    source: 'Source/NXVideo/NXImageLayerVideo.h:199'
  - symbol: NXImageLayerVideo.ScreenToWorld
    declaration: 'bool		ScreenToWorld(XVertex2d^ ptScreen, [OutAttribute] XVertex2d^% ptWorld);'
    source: 'Source/NXVideo/NXImageLayerVideo.h:205'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
