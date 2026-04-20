---
title: Video Helper Processing Recipes
description: Common helper-class tasks for video filters, grouped channels, mosaics, and stabilizers.
tags:
  - howto
  - videoview
  - video-helper
sources:
  - workflows/wf-api-videoview.md
---

# Video Helper Processing Recipes

## What This Recipe Covers
- Use `XVideoFrameFilter` for helper-side channel filtering and cleanup.
- Use `XVideoGroup` for grouped channels, muxing, output URLs, and metadata handlers.
- Use `XVideoMosaic` for mosaic image composition and frame-parameter inspection.
- Use `XVideoStabilizer` for stabilization pipelines that still depend on channel binding and frame-parameter access.

## Use This Recipe For
- The user asks about video helper, filter, group, mosaic, or stabilizer classes rather than normal playback.
- The user asks about grouped video metadata callbacks, output URLs, or helper-side frame parameters.

## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the question is just normal playback/channel binding, go back to the main `VideoView` playback recipe instead of overusing these helper classes.

## Common Recipes
- `비디오 필터`
  A typical helper flow is: `SetVideoChannel`, then `FilterProcess`, and `CleanUp` when the helper lifecycle ends.
- `비디오 그룹`
  For grouped output, a typical flow is `SetVideoChannels`, then `OpenOutputUrl` / `StartMuxing`, with `Pause` / `Resume` / `StopMuxing` for runtime control.
- `비디오 그룹 메타데이터`
  Use `SetGroupMetadAddHandler` or `SetGroupMetadUpdateHandler` when the question is about metadata callbacks rather than rendering.
- `모자이크`
  A typical mosaic explanation uses `SetVideoChannel`, `SetMosaicImage`, and `GetFrameParams`; `ResetMosaic` or `ResetVideoChannel` clears state.
- `안정화`
  A typical stabilization flow is `SetVideoChannel`, then `Feed`, inspect `GetFrameParams`, and `Reset` when reinitializing the stabilizer.

## Related Pages
- [VideoView API Workflow](../../workflows/wf-api-videoview.md)
- [VideoView Playback and KLV Recipes](videoview-playback-and-klv.md)
- [Video Channel, KLV, and Fusion](../concepts/video-channel-klv-and-fusion.md)
