---
title: Pixoneer.NXDL.NXVideo.NXVideoView Methods
aliases:
  - NXVideoView Methods
  - Pixoneer.NXDL.NXVideo.NXVideoView
  - NXVideoView
symbols:
  - NXVideoView
  - AddRenderLayer
  - CallDrawLastFrame
  - CaptureFrame
  - EnableVideoFusion
  - GetDrawArgs
  - GetHandle
  - GetScreenPixel
  - GetVideoChannel
  - GetWorldPixel
  - IsUnderMouse
  - RefreshScreen
  - RemoveRenderLayer
  - RequestRender
  - ResetVideoChannel
  - ResetVideoChannelFuse
  - ScreenToWorld
  - SetFusionReference
  - SetFusionWithSensorModel
  - SetUnderMouse
  - SetVideoChannel
  - SetVideoChannelFuse
  - SetVigentte
  - SpaceToWorld
  - TrimFuseChannel
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
- Type: `NXVideoView`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_NXVideoView.htm`
- Type declaration: `Source/NXVideo/NXVideoView.h:152`
- Method count: `26`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.NXVideoView
type_name: NXVideoView
namespace: Pixoneer.NXDL.NXVideo
method_section_prefix: "## "
verification_rules:
  - treat_declaration_lines_as_symbol_existence_evidence
  - treat_implementation_lines_as_source_anchor_evidence
  - use_this_page_only_after_a_workflow_or_type_hint_narrows_scope
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page only as a verification layer after a workflow or explicit type hint identifies the target type.
- Cross-check declaration and implementation lines when overloads, properties, or call shapes matter.
- Do not synthesize end-to-end usage answers from this page alone.
## AddRenderLayer
- Description: 뷰에 레이어를 추가한다.
- Declaration: `Source/NXVideo/NXVideoView.h:218`, `Source/NXVideo/NXVideoView.h:224`
- Implementation: `Source/NXVideo/NXVideoView.cpp:359`, `Source/NXVideo/NXVideoView.cpp:364`

## CallDrawLastFrame
- Description: 비디오 프레임을 다른 화면에 그리기 위하여 렌더링 요청을 한다. 이 때 모든 모델/투영 행렬은 설정이 완료된 상태라고 가정하고 입력되는 좌표로 직접 그리기 명령을 내보낸다. Warping 효과를 주기 위하여 격자 형태의 좌표를 입력받는데 테두리 점들이 반드시 입력에 포함되어야 한다.
- Declaration: `Source/NXVideo/NXVideoView.h:373`
- Implementation: `Source/NXVideo/NXVideoView.cpp:878`

## CaptureFrame
- Description: 화면에 그린 비디오 프레임을 텍스처로 얻는다.
- Declaration: `Source/NXVideo/NXVideoView.h:381`
- Implementation: `Source/NXVideo/NXVideoView.cpp:929`

## EnableVideoFusion
- Description: 영상 융합 활성화 여부를 설정한다. 융합이 활성화되면 융합 영상이 도시된다.
- Declaration: `Source/NXVideo/NXVideoView.h:548`
- Implementation: `Source/NXVideo/NXVideoView.cpp:1094`

## GetDrawArgs
- Description: 비디오뷰 그리기 인자를 얻는다.
- Declaration: `Source/NXVideo/NXVideoView.h:202`
- Implementation: `Source/NXVideo/NXVideoView.cpp:435`

## GetHandle
- Description: 비디오뷰 윈도 핸들을 얻는다.
- Declaration: `Source/NXVideo/NXVideoView.h:189`
- Implementation: `Source/NXVideo/NXVideoView.cpp:87`

## GetScreenPixel
- Description: 비디오뷰 패널 화면 좌표에 해당하는 화소 색상값을 얻는다. 프레임 영역 밖인 경우 배경 색상을 반환한다.
- Declaration: `Source/NXVideo/NXVideoView.h:340`
- Implementation: `Source/NXVideo/NXVideoView.cpp:838`

## GetVideoChannel
- Description: 비디오뷰에 설정한 채널을 얻는다.
- Declaration: `Source/NXVideo/NXVideoView.h:362`
- Implementation: `Source/NXVideo/NXVideoView.cpp:421`

## GetWorldPixel
- Description: 비디오뷰 영상(World) 좌표에 해당하는 화소 색상값을 얻는다. 프레임 영역 밖인 경우 배경 색상을 반환한다.
- Declaration: `Source/NXVideo/NXVideoView.h:344`
- Implementation: `Source/NXVideo/NXVideoView.cpp:850`

## IsUnderMouse
- Description: 이 비디오뷰가 마우스 커서 아래에 있는지 확인한다.
- Declaration: `Source/NXVideo/NXVideoView.h:210`
- Implementation: `not found`

## RefreshScreen
- Description: 스크린을 갱신한다.
- Declaration: `Source/NXVideo/NXVideoView.h:193`
- Implementation: `Source/NXVideo/NXVideoView.cpp:259`

## RemoveRenderLayer
- Description: 뷰에 레이어를 분리한다.
- Declaration: `Source/NXVideo/NXVideoView.h:230`
- Implementation: `Source/NXVideo/NXVideoView.cpp:381`

## RequestRender
- Description: 렌더 요청 식별자를 지정하여 화면 갱신을 요청한다. 갈무리 버퍼가 연결된 경우 지정한 식별자가 갈무리 버퍼 프레임 식별자로 설정된다.
- Declaration: `Source/NXVideo/NXVideoView.h:198`
- Implementation: `Source/NXVideo/NXVideoView.cpp:266`

## ResetVideoChannel
- Description: 비디오뷰에 설정한 채널을 없앤다.
- Declaration: `Source/NXVideo/NXVideoView.h:359`
- Implementation: `Source/NXVideo/NXVideoView.cpp:415`

## ResetVideoChannelFuse
- Description: 영상 융합 보조 채널을 해제한다.
- Declaration: `Source/NXVideo/NXVideoView.h:544`
- Implementation: `Source/NXVideo/NXVideoView.cpp:1088`

## ScreenToWorld
- Description: 비디오뷰 패널 화면(Screen) 화소 좌표를 비디오뷰 영상(World) 좌표로 변환한다.
- Declaration: `Source/NXVideo/NXVideoView.h:334`
- Implementation: `Source/NXVideo/NXVideoView.cpp:823`

## SetFusionReference
- Description: 영상 융합을 위한 정합 참조 정보를 설정한다. 영상 중심점이 일치한다고 가정하고 두 영상의 화각만 지정한다.
- Declaration: `Source/NXVideo/NXVideoView.h:564`, `Source/NXVideo/NXVideoView.h:570`, `Source/NXVideo/NXVideoView.h:576`
- Implementation: `Source/NXVideo/NXVideoView.cpp:1112`, `Source/NXVideo/NXVideoView.cpp:1122`, `Source/NXVideo/NXVideoView.cpp:1135`

## SetFusionWithSensorModel
- Description: 영상 융합에서 영상 정합을 위한 센서모델 사용 여부를 설정한다.
- Declaration: `Source/NXVideo/NXVideoView.h:552`
- Implementation: `Source/NXVideo/NXVideoView.cpp:1100`

## SetUnderMouse
- Description: 이 비디오뷰가 마우스 커서 아래에 있는 상태를 설정한다. 내부 엔진에서 호출되며 사용자가 호출할 필요가 없다.
- Declaration: `Source/NXVideo/NXVideoView.h:206`
- Implementation: `not found`

## SetVideoChannel
- Description: 비디오뷰에 재생할 비디오 채널을 설정한다.
- Declaration: `Source/NXVideo/NXVideoView.h:351`, `Source/NXVideo/NXVideoView.h:356`
- Implementation: `Source/NXVideo/NXVideoView.cpp:394`, `Source/NXVideo/NXVideoView.cpp:408`

## SetVideoChannelFuse
- Description: 영상 융합 보조 채널을 설정한다.
- Declaration: `Source/NXVideo/NXVideoView.h:542`
- Implementation: `Source/NXVideo/NXVideoView.cpp:1082`

## SetVigentte
- Description: 비네팅 효과 완화 필터를 설정한다.
- Declaration: `Source/NXVideo/NXVideoView.h:582`
- Implementation: `Source/NXVideo/NXVideoView.cpp:1143`

## SpaceToWorld
- Description: 현재 프레임에서 지구상의 지리공간(Space) 좌표를 비디오뷰 영상(World) 좌표로 변환한다.
- Declaration: `Source/NXVideo/NXVideoView.h:271`, `Source/NXVideo/NXVideoView.h:279`, `Source/NXVideo/NXVideoView.h:315`, `Source/NXVideo/NXVideoView.h:322`
- Implementation: `Source/NXVideo/NXVideoView.cpp:707`, `Source/NXVideo/NXVideoView.cpp:723`, `Source/NXVideo/NXVideoView.cpp:778`, `Source/NXVideo/NXVideoView.cpp:793`

## TrimFuseChannel
- Description: 영상 융합 보조 채널의 불필요한 외곽영역을 제거한다.
- Declaration: `Source/NXVideo/NXVideoView.h:559`
- Implementation: `Source/NXVideo/NXVideoView.cpp:1106`

## WorldToScreen
- Description: 비디오뷰 영상(World) 좌표를 비디오뷰 패널 화면(Screen) 화소 좌표로 변환한다.
- Declaration: `Source/NXVideo/NXVideoView.h:328`
- Implementation: `Source/NXVideo/NXVideoView.cpp:808`

## WorldToSpace
- Description: 현재 프레임에서 비디오뷰 영상(World) 좌표를 지구상의 지리공간(Space) 좌표로 변환한다.
- Declaration: `Source/NXVideo/NXVideoView.h:238`, `Source/NXVideo/NXVideoView.h:247`, `Source/NXVideo/NXVideoView.h:255`, `Source/NXVideo/NXVideoView.h:264`, `Source/NXVideo/NXVideoView.h:286`, `Source/NXVideo/NXVideoView.h:294`, `Source/NXVideo/NXVideoView.h:301`, `Source/NXVideo/NXVideoView.h:309`
- Implementation: `Source/NXVideo/NXVideoView.cpp:667`, `Source/NXVideo/NXVideoView.cpp:672`, `Source/NXVideo/NXVideoView.cpp:687`, `Source/NXVideo/NXVideoView.cpp:692`, `Source/NXVideo/NXVideoView.cpp:738`, `Source/NXVideo/NXVideoView.cpp:743`, `Source/NXVideo/NXVideoView.cpp:758`, `Source/NXVideo/NXVideoView.cpp:763`
