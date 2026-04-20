---
title: VideoView Playback and KLV Recipes
description: Common video tasks for open, bind, render, capture, and KLV extraction.
tags:
  - howto
  - videoview
  - video
sources:
  - workflows/wf-api-videoview.md
  - workflows/wf-api-imageview.md
---

# VideoView Playback and KLV Recipes

## What This Recipe Covers
- Open TS or other video files through `XVideoIO`.
- Bind a channel to `NXVideoView` and refresh or request render.
- Capture the current frame and extract KLV metadata from MPEG2 TS packets.
- Explain when to use `NXImageLayerVideo` instead of `NXVideoView`.

## Use This Recipe For
- The user asks how to show a video on screen.
- The user asks how to bind or reset channels.
- The user asks about frame capture, KLV, or video fusion.


## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.

## Common Recipes
- `TS 파일 재생`
  A typical answer flow is: `XVideoIO.OpenFile`, then bind the result with `SetVideoChannel`, then mention `RefreshScreen` or `RequestRender`.
- `채널 해제`
  Use `ResetVideoChannel` instead of treating it as a view-layer removal task.
- `현재 프레임 캡처`
  Use `CaptureFrame` when the question is about the live video output itself.
- `KLV 추출`
  Use `NXMpegTSAnalysis.GetKLVMetaData` when the payload is still at TS packet level.
- `embedded video layer`
  If the user names `ImageView/MilmapView/PlanetView` but the task is channel wiring or initial frame sizing, answer with `NXImageLayerVideo` or sibling video-layer APIs from the video family.
- `video helper classes`
  `XVideoFrameFilter`, `XVideoGroup`, `XVideoMosaic`, and `XVideoStabilizer` are for filtering, grouped channels, mosaics, and stabilization rather than basic playback.

## Related Pages
- [VideoView API Workflow](../../workflows/wf-api-videoview.md)
- [ImageView API Workflow](../../workflows/wf-api-imageview.md)
- [Video Channel, KLV, and Fusion](../concepts/video-channel-klv-and-fusion.md)
