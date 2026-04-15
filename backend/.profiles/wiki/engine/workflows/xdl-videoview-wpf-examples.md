---
title: XDL VideoView WPF Examples
aliases:
  - XDL_VideoView01_wpf
  - XDL_VideoView02_wpf
  - XDL_VideoView03_wpf
  - XDL_VideoView04_wpf
  - XDL_VideoView05_wpf
symbols:
  - NXVideoView
  - NXVideoLayerOverlay
  - XVideoIO
  - XVideo
  - XVideoChannel
tags:
  - engine
  - workflow
  - samples
  - wpf
  - video
---

# Overview
- Sample root: `C:/Users/p22418/Documents/Amaranth10/nxdl_example`
- These examples cover TS-file playback, playback state control, overlay rendering, timeline UI, and frame enhancement/capture.
- Common references:
  - `NXDL`
  - `NXVideo`
  - optional `NXDLgr`, `NXDLsm`
  - `WindowsFormsIntegration`

# Case Map
- `XDL_VideoView01_wpf`
  - Simplest menu-driven playback sample
  - Opens TS files through `XVideoIO.OpenFile(..., "XFFMPDRIVER", ...)`
  - Exposes menu actions for play / pause / stop / resume

- `XDL_VideoView02_wpf`
  - Button-driven playback shell
  - Adds explicit `VideoState`
  - Includes `NXVideoLayerOverlay`
  - Uses play/pause/stop buttons with image assets

- `XDL_VideoView03_wpf`
  - Timeline-aware playback shell
  - Adds current/total frame tracking
  - Synchronizes playback state with a slider/label UI

- `XDL_VideoView04_wpf`
  - Playback plus view/enhancement operations
  - Adds zoom, rotate, flip, shift, gamma/brightness/contrast, algorithm toggles
  - Adds frame capture actions

- `XDL_VideoView05_wpf`
  - Advanced video shell with extra graphics/simulation references
  - Observed additional dependencies: `NXDLgr`, `NXDLsm`
  - Keeps the timeline/enhancement/capture pattern and extends the surrounding environment

# Delivery Notes
- `XDL_VideoView03_wpf` and later samples should be treated as multi-part WPF UI examples, not bare code snippets.
- If the user asks for a "full player" rather than a minimal playback demo, prefer the later samples because they include timeline and enhancement UI, not only file open/play calls.
## Structured Page Facts
```yaml
page_family: sample_workflow_examples
role: curated_reference
verification_rules:
  - use_this_page_when_the_question_matches_its_scenario_scope
  - cross_check_methods_pages_before_emitting_exact_call_shapes
  - keep_output_shape_rules_from_this_page_when_present
```

## Runtime Usage
- Use this page as a richer scenario-level reference than the normalized `wf-*.md` pages when the question clearly matches this scenario.
- If this page defines output-shape constraints such as WPF/XAML delivery, keep those constraints in the final answer.
- Do not use sample-driven code patterns here to override conflicting exact signatures from methods pages.
