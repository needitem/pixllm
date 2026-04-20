---
title: VideoView API Workflow
description: Open video, bind channels, capture frames, extract KLV, and explain embedded video-layer handling.
aliases:
  - videoview api
  - videoview 사용법
  - mpeg2ts playback
  - video channel bind
  - klv metadata extract
  - videoview frame capture
  - video fusion
  - mpeg2ts 동영상 파일을 로드해서 화면에 도시
  - videoview에 비디오 채널 연결
  - videoview 현재 프레임 캡처
  - mpeg2ts에서 klv 메타데이터 추출
  - imageview 안에 비디오 레이어 연결
  - imageview 안에 비디오 레이어를 연결하는 방법
  - imageview video layer
  - video image layer
  - videoview에서 영상 융합 활성화
  - imageview 비디오 레이어에 채널 연결하는 방법
  - imageview 비디오 레이어 채널 해제하는 방법
  - imageview 비디오 레이어 초기 프레임 크기 설정 방법
  - imageview 비디오 레이어 화면 좌표를 실제 좌표로 변환하는 방법
  - imageview 비디오 레이어에서 to 실제 좌표 사용하는 방법
  - imageview 비디오 레이어에서 to 공간 사용하는 방법
  - imageview 비디오 레이어에서 to 영상 사용하는 방법
  - imageview 비디오 레이어에서 to 화면 좌표 사용하는 방법
  - milmapview에서 동영상 채널 초기화
  - milmapview 비디오 레이어 사용법
  - planetview에서 동영상 채널 초기화
  - planetview 비디오 레이어 사용법
  - milmapview에서 동영상 프레임 설정
  - planetview에서 동영상 프레임 설정
  - 비디오 필터에서 up 사용
  - 비디오 그룹에서 group metad add handler 설정
symbols:
  - NXVideoView
  - XVideoIO
  - XVideo
  - XVideoChannel
  - NXMpegTSAnalysis
  - NXImageLayerVideo
  - NXMilmapLayerVideoBase
  - NXPlanetLayerVideoBase
  - XVideoGroup
  - XVideoMosaic
  - XVideoStabilizer
  - XVideoFrameFilter
tags:
  - engine
  - workflow
  - api
  - video
---

# Overview
- Goal: cover open/bind/render/capture/KLV questions for the video family.
- This workflow covers `XVideoIO`, `NXVideoView`, `NXImageLayerVideo`, and `NXMpegTSAnalysis`.
- For the current wiki routing, even when `ImageView` is explicitly named, `비디오 레이어`, `채널 연결/해제`, `초기 프레임 크기`, and video-layer screen/world conversion are treated as `VideoView`.
- The same routing rule applies when `MilmapView` or `PlanetView` is named and the intent is video channel wiring, KLV, frame capture, or embedded video-layer conversion.

## Primary Usage Buckets
- `동영상 열기`: `XVideoIO.OpenFile`
- `화면 표시`: `SetVideoChannel`, `ResetVideoChannel`, `RefreshScreen`, `RequestRender`
- `프레임 캡처`: `CaptureFrame`
- `KLV`: `NXMpegTSAnalysis.GetKLVMetaData`
- `ImageView 안의 비디오`: `NXImageLayerVideo.SetVideoChannel`, `ResetVideoChannel`, `SetInitialFrameSize`
- `영상 융합`: `SetVideoChannelFuse`, `EnableVideoFusion`

## Practical Answer Shape
- `파일 열기 + 표시`: `OpenFile` -> `SetVideoChannel` -> `RefreshScreen/RequestRender`
- `채널 교체/해제`: `SetVideoChannel`과 `ResetVideoChannel`을 같은 흐름 안에서 설명
- `프레임 캡처`: live view 캡처인지, embedded video layer인지 먼저 나눈 뒤 `CaptureFrame` 또는 layer-side API를 제시
- `embedded video layer`: `NXImageLayerVideo` 계열은 view family가 아니라 video family 책임으로 설명
- `필터/그룹/모자이크/안정화`: low-level helper가 나오면 `XVideoFrameFilter`, `XVideoGroup`, `XVideoMosaic`, `XVideoStabilizer`를 묶어 답합니다


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

## Knowledge Bundle
```yaml
concept_terms:
- video channel
- klv
- frame capture
- fusion
routing_hints:
- all_of: [imageview, 비디오 레이어]
- all_of: [imageview, 비디오 레이어]
  any_of: [채널, 프레임, 영상, 공간, 화면, 실제 좌표]
- all_of: [imageview, 동영상 채널]
- all_of: [imageview, 동영상 프레임]
- all_of: [milmapview, 동영상 채널]
- all_of: [milmapview, 동영상 프레임]
- all_of: [milmapview]
  any_of: [동영상 채널, 동영상 프레임, 비디오 레이어]
- all_of: [planetview, 동영상 채널]
- all_of: [planetview, 동영상 프레임]
- all_of: [planetview]
  any_of: [동영상 채널, 동영상 프레임, 비디오 레이어]
bundle_pages:
- path: pages/howtos/videoview-playback-and-klv.md
  relation: family_howto
- path: pages/howtos/video-helper-processing-recipes.md
  relation: family_howto
- path: pages/concepts/video-channel-klv-and-fusion.md
  relation: family_concept
- path: workflows/wf-api-imageview.md
  relation: dependency_workflow
- path: pages/sources/nxvideo.md
  relation: source_summary
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-20T02:38:44Z`.
- Resolved required symbols: `13/13`
- Linked modules:
  - `NXVideo`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
```yaml
workflow_family: api_videoview
output_shape: workflow_bound_to_host_context
required_symbols:
  - XVideoIO.OpenFile
  - NXVideoView.SetVideoChannel
  - NXVideoView.ResetVideoChannel
  - NXVideoView.RefreshScreen
  - NXVideoView.RequestRender
  - NXVideoView.AddRenderLayer
  - NXVideoView.CaptureFrame
  - NXMpegTSAnalysis.GetKLVMetaData
  - NXImageLayerVideo.SetVideoChannel
  - NXImageLayerVideo.ResetVideoChannel
  - NXImageLayerVideo.SetInitialFrameSize
  - NXImageLayerVideo.ScreenToWorld
  - NXImageLayerVideo.WorldToScreen
required_facts:
  - symbol: XVideoIO.OpenFile
    declaration: 'NXVideo::XVideo^ OpenFile(String^ strFilePath, String^ strDriverName, [OutAttribute] String^% strError);'
    source: 'Source/NXVideo/XVideoIO.h:432'
  - symbol: NXVideoView.SetVideoChannel
    declaration: 'bool SetVideoChannel(XVideo^ video, int channelIndex);'
    source: 'Source/NXVideo/NXVideoView.h:351'
  - symbol: NXVideoView.ResetVideoChannel
    declaration: 'void ResetVideoChannel();'
    source: 'Source/NXVideo/NXVideoView.h:359'
  - symbol: NXVideoView.RefreshScreen
    declaration: 'bool RefreshScreen();'
    source: 'Source/NXVideo/NXVideoView.h:193'
  - symbol: NXVideoView.RequestRender
    declaration: 'void RequestRender(UInt64 requestID);'
    source: 'Source/NXVideo/NXVideoView.h:198'
  - symbol: NXVideoView.AddRenderLayer
    declaration: 'bool AddRenderLayer(NXVideoLayer^ layer);'
    source: 'Source/NXVideo/NXVideoView.h:218'
  - symbol: NXVideoView.CaptureFrame
    declaration: 'cli::array<XTexture^>^ CaptureFrame(bool bPrimaryOnly);'
    source: 'Source/NXVideo/NXVideoView.h:381'
  - symbol: NXMpegTSAnalysis.GetKLVMetaData
    declaration: 'bool GetKLVMetaData(cli::array<unsigned char>^ packet_data, int length, [OutAttribute] cli::array<unsigned char>^% meta_data);'
    source: 'Source/NXVideo/NXMpegTSAnalysis.h:41'
  - symbol: NXImageLayerVideo.SetVideoChannel
    declaration: 'void SetVideoChannel(XVideoChannel^ channel);'
    source: 'Source/NXVideo/NXImageLayerVideo.h:61'
  - symbol: NXImageLayerVideo.ResetVideoChannel
    declaration: 'void ResetVideoChannel();'
    source: 'Source/NXVideo/NXImageLayerVideo.h:64'
  - symbol: NXImageLayerVideo.SetInitialFrameSize
    declaration: 'void SetInitialFrameSize(int width, int height);'
    source: 'Source/NXVideo/NXImageLayerVideo.h:71'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_runtime_methods_index_before_emitting_code
```


