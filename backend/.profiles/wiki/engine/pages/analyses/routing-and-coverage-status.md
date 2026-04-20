---
title: Routing and Coverage Status
description: Current routing quality and answer-material coverage status for the engine wiki.
tags:
  - analysis
  - routing
  - coverage
  - wiki
---

# Routing and Coverage Status

## Summary
- The current engine wiki is strong enough for many representative API-usage questions.
- It is not yet strong enough to claim full coverage for every possible question.
- Classification quality is very high on the curated API-family set and noticeably lower on low-signal paraphrase/stress questions.
- Data coverage is deepest in `ImageView`, `Raster/XDM`, `VideoView`, and `Coordinate`.
- The remaining weak zone is mostly not “missing family pages”, but `low-signal question wording`, `editor exactness`, and `rare low-level APIs`.

## Evaluation Basis
- Curated API-family set (`130` questions): `top1 129/130 = 99.23%`, `top5 99.23%`
- Paraphrase sample (`355` questions): `top1 304/355 = 85.63%`, `top5 336/355 = 94.65%`
- Balanced stress batch (`10000` questions, older full run): `top1 7283/10000 = 72.83%`, `top5 84.62%`

## Where Routing Is Strong
- Curated family routing is effectively solved for:
  - `Raster/XDM`
  - `Coordinate`
  - `VideoView`
  - `MilmapView`
  - `PlanetView`
  - `Vector`
  - `Editor`
  - `Scene Editor`
  - `Sensor Model`
  - `DFS`
  - `UspaceView`
  - `Core Utils`
- `ImageView` is also strong, but still shows an occasional transport/no-result outlier in the curated set.

## Family Status
| Family | Curated 130 | Paraphrase 355 | 10k Stress | Data Richness | Notes |
|---|---:|---:|---:|---|---|
| `ImageView` | `0.90` | `0.8667` | `0.6341` | High | Strong workflow, howto, concepts, and source anchors. Still sensitive to low-signal wording such as `맞춤 보기` or `Test 사용`. |
| `Raster/XDM` | `1.00` | `0.84` | `0.7908` | High | Best covered family. Strong declarations, recipes, and many common questions already fit this family well. |
| `VideoView` | `1.00` | `0.8444` | `0.7041` | High | Good on normal playback/channel/KLV questions. Harder when the question hides the family behind generic helper names. |
| `Coordinate` | `1.00` | `1.00` | `0.7161` | High | Strong for explicit SR/code/point-transform questions. Still competes with other families when wording gets generic. |
| `Vector` | `1.00` | `1.00` | `0.7761` | Medium | Good on explicit vector metadata, driver-key, overlay, and hit-test questions. |
| `MilmapView` | `1.00` | `0.90` | `0.6279` | Medium | Good on explicit view-control questions. Harder on shader-style or mixed display wording. |
| `PlanetView` | `1.00` | `0.90` | `0.6431` | Medium | Good on explicit camera/dataset questions. Harder on shader/cartoon/environment wording. |
| `DFS` | `1.00` | `n/a` | `n/a` | Medium | Export/progress/cancel and provider-group flows are covered, but long-tail DFS/provider phrasing can still drift into view families. |
| `Sensor Model` | `1.00` | `n/a` | `n/a` | Medium | Strong for image-center and image/ground projection. |
| `UspaceView` | `1.00` | `n/a` | `n/a` | Medium | Strong for explicit `UspaceView` space/world/screen questions. |
| `Scene Editor` | `1.00` | `n/a` | `n/a` | Medium | Good for scene lifecycle/select/hit-test. |
| `Editor` | `1.00` | `1.00` | `0.5568` | Medium-Low | Good routing on curated questions, but exact grounding is weaker because runtime methods index does not currently resolve this family directly. |
| `Core Utils` | `1.00` | `n/a` | `n/a` | Medium | Narrow family with good focused answers for license/config/progress. |

## Where Data Is Deep
- These families usually have enough material to answer a normal usage question with:
  - workflow
  - howto
  - concept
  - source summary
- Deepest families:
  - `Raster/XDM`
  - `ImageView`
  - `VideoView`
  - `Coordinate`

## Where Data Is Still Thin
- `Editor`
  - Better document structure now, but still more doc-backed than source-grounded.
- `MilmapView` / `PlanetView`
  - Good for normal view operations, but shader/effect/environment questions remain thinner.
- `DFS`
  - Export/control flow is decent, but broader provider/dataset recipes could still be denser.

## Hard Question Patterns
- `Low-signal paraphrase`
  - Examples:
    - `Up 사용`
    - `Test 사용`
    - `맞춤 보기`
  - Problem:
    - The wording often drops the API family entirely.
- `Embedded video inside another view`
  - Examples:
    - `ImageView 비디오 레이어 ...`
    - `MilmapView에서 동영상 채널 초기화`
    - `PlanetView에서 동영상 프레임 설정`
  - Problem:
    - The visible host view and the actual owning API family are different.
- `Raster low-level parameter questions`
  - Examples:
    - `Input Param`
    - `Color Table`
    - `Change Statistics`
    - `Darkness Level`
    - `RPC Model`
  - Problem:
    - The question names a low-level concept but does not say whether the user means raster processing, display, coordinate projection, or helper utilities.
- `Planet/Milmap shader-effect questions`
  - Examples:
    - `Shader Code Basso`
    - `Cartoon Effect`
    - `Sun Follow`
  - Problem:
    - These often look like rendering concepts instead of clearly belonging to one view family.

## Representative Failure Examples
- `맞춤 보기 샘플 코드로 설명해줘 예제 코드 보여줘`
  - Expected: `ImageView`
  - Actual: `Coordinate`
  - Why hard: no `ImageView` or display-shell words remain.
- `Test 사용 샘플 코드로 설명해줘하려면 어떻게 해야 해?`
  - Expected: `ImageView`
  - Actual: `Editor`
  - Why hard: the signal is almost entirely gone.
- `XDL에서 To 영상 사용할 때 필요한 API가 뭐야? 예제 코드 보여줘`
  - Expected: `VideoView`
  - Actual: `ImageView`
  - Why hard: embedded video-layer wording is partially stripped.
- `Shader Code Basso 사용 샘플 코드로 설명해줘 절차 알려줘`
  - Expected: `MilmapView`
  - Actual: `Coordinate`
  - Why hard: the question does not retain the view-family owner strongly enough.
- `C#에서 Cartoon Effect 확인하려면 어떻게 해야 해?하려면 어떻게 해야 해?`
  - Expected: `PlanetView`
  - Actual: `MilmapView`
  - Why hard: effect name remains, but family signal is weak.

## Practical Bottom Line
- The current wiki is strong enough to answer many normal engine usage questions.
- It is not yet strong enough to claim “all questions are sufficiently covered”.
- Remaining work is less about creating entirely new family pages and more about:
  - densifying low-signal recipes
  - improving editor exact grounding
  - filling rare low-level API recipes
  - reducing ambiguity where host view and owning API family differ

## Recommended Next Focus
- `Editor` exactness and stronger source-level grounding
- `Video helper / embedded video-layer` recipes
- `Milmap/Planet shader-effect` recipes
- `Raster low-level parameter` recipes
- Additional low-signal `howto` pages that preserve family cues in the answer path
