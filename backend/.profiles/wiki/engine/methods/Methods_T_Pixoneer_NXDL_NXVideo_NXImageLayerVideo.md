---
title: Pixoneer.NXDL.NXVideo.NXImageLayerVideo Methods
aliases:
  - NXImageLayerVideo Methods
  - Pixoneer.NXDL.NXVideo.NXImageLayerVideo
  - NXImageLayerVideo
symbols:
  - NXImageLayerVideo
  - ImageToWorld
  - ResetVideoChannel
  - ScreenToWorld
  - SetInitialFrameSize
  - SetVideoChannel
  - SetVideoFrame
  - SpaceToWorld
  - WorldToImage
  - WorldToScreen
  - WorldToSpace
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nxvideo
---

# Overview
- Namespace: `Pixoneer.NXDL.NXVideo`
- Type: `NXImageLayerVideo`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_NXImageLayerVideo.htm`
- Type declaration: `Source/NXVideo/NXImageLayerVideo.h:38`
- Method count: `10`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.NXImageLayerVideo
type_name: NXImageLayerVideo
namespace: Pixoneer.NXDL.NXVideo
method_section_prefix: "## "
verification_rules:
  - treat_declaration_lines_as_symbol_existence_evidence
  - treat_implementation_lines_as_source_anchor_evidence
  - prefer_this_page_over_examples_for_exact_call_shapes
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page to verify exact symbol existence before emitting code.
- Cross-check declaration and implementation lines when overloads or call shapes matter.
- Treat examples and workflow pages as composition guidance, but treat this page as the canonical member list.
## ImageToWorld
- Description: 비디오 영상(Image) 좌표를 이미지뷰(World) 좌표(PIXEL)로 변환한다.
- Declaration: `Source/NXVideo/NXImageLayerVideo.h:97`
- Implementation: `Source/NXVideo/NXImageLayerVideo.cpp:185`

## ResetVideoChannel
- Description: 레이어에 연결된 채널을 제거한다.
- Declaration: `Source/NXVideo/NXImageLayerVideo.h:64`
- Implementation: `Source/NXVideo/NXImageLayerVideo.cpp:75`

## ScreenToWorld
- Description: 이미지뷰 패널 화면(Screen) 화소 좌표를 이미지뷰(World) 좌표로 변환한다.
- Declaration: `Source/NXVideo/NXImageLayerVideo.h:205`
- Implementation: `Source/NXVideo/NXImageLayerVideo.cpp:412`

## SetInitialFrameSize
- Description: 레이어에서 표시할 영상 프레임 크기를 설정한다. 동영상 채널이 설정되어 있으면 이 요청은 무시되고 채널 동영상 크기로 자동 설정된다.
- Declaration: `Source/NXVideo/NXImageLayerVideo.h:71`
- Implementation: `Source/NXVideo/NXImageLayerVideo.cpp:81`

## SetVideoChannel
- Description: 레이어에서 표시할 동영상 채널을 설정한다.
- Declaration: `Source/NXVideo/NXImageLayerVideo.h:61`
- Implementation: `Source/NXVideo/NXImageLayerVideo.cpp:61`

## SetVideoFrame
- Description: 레이어에서 표시할 영상 프레임을 설정한다. 동영상 채널이 먼저 설정된 경우 프레임 설정 요청은 무시된다.
- Declaration: `Source/NXVideo/NXImageLayerVideo.h:57`
- Implementation: `Source/NXVideo/NXImageLayerVideo.cpp:52`

## SpaceToWorld
- Description: 현재 프레임에서 지구상의 지리공간(Space) 좌표를 이미지뷰(World) 좌표로 변환한다.
- Declaration: `Source/NXVideo/NXImageLayerVideo.h:144`, `Source/NXVideo/NXImageLayerVideo.h:151`, `Source/NXVideo/NXImageLayerVideo.h:187`, `Source/NXVideo/NXImageLayerVideo.h:193`
- Implementation: `Source/NXVideo/NXImageLayerVideo.cpp:278`, `Source/NXVideo/NXImageLayerVideo.cpp:299`, `Source/NXVideo/NXImageLayerVideo.cpp:362`, `Source/NXVideo/NXImageLayerVideo.cpp:383`

## WorldToImage
- Description: 이미지뷰(World) 좌표(PIXEL)를 비디오 영상(Image) 좌표로 변환한다.
- Declaration: `Source/NXVideo/NXImageLayerVideo.h:103`
- Implementation: `Source/NXVideo/NXImageLayerVideo.cpp:205`

## WorldToScreen
- Description: 이미지뷰(World) 좌표를 이미지뷰 패널 화면(Screen) 화소 좌표로 변환한다.
- Declaration: `Source/NXVideo/NXImageLayerVideo.h:199`
- Implementation: `Source/NXVideo/NXImageLayerVideo.cpp:393`

## WorldToSpace
- Description: 현재 프레임에서 이미지뷰(World) 좌표를 지구상의 지리공간(Space) 좌표로 변환한다.
- Declaration: `Source/NXVideo/NXImageLayerVideo.h:111`, `Source/NXVideo/NXImageLayerVideo.h:120`, `Source/NXVideo/NXImageLayerVideo.h:128`, `Source/NXVideo/NXImageLayerVideo.h:137`, `Source/NXVideo/NXImageLayerVideo.h:158`, `Source/NXVideo/NXImageLayerVideo.h:166`, `Source/NXVideo/NXImageLayerVideo.h:173`, `Source/NXVideo/NXImageLayerVideo.h:181`
- Implementation: `Source/NXVideo/NXImageLayerVideo.cpp:225`, `Source/NXVideo/NXImageLayerVideo.cpp:230`, `Source/NXVideo/NXImageLayerVideo.cpp:252`, `Source/NXVideo/NXImageLayerVideo.cpp:257`, `Source/NXVideo/NXImageLayerVideo.cpp:309`, `Source/NXVideo/NXImageLayerVideo.cpp:314`, `Source/NXVideo/NXImageLayerVideo.cpp:336`, `Source/NXVideo/NXImageLayerVideo.cpp:341`
