---
title: Pixoneer.NXDL.NXVideo.XVideo Methods
aliases:
  - XVideo Methods
  - Pixoneer.NXDL.NXVideo.XVideo
  - XVideo
symbols:
  - XVideo
  - Close
  - GetChannel
  - GetChannelProxy
  - GetLastError
  - GetNativeVideo
  - GetNumChannels
  - GetNumStreams
  - Pause
  - PtsToStreamTime
  - Resume
  - Seek
  - StreamTimeToPts
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
- Type: `XVideo`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XVideo.htm`
- Type declaration: `Source/NXVideo/XVideo.h:28`
- Method count: `12`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XVideo
type_name: XVideo
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
## Close
- Description: 현재 Video 스트림을 닫는다. 개발자는 이 함수를 부르기 전에 NXVideoView 객체를 호출해야 한다.
- Declaration: `Source/NXVideo/XVideo.h:57`
- Implementation: `Source/NXVideo/XVideo.cpp:111`

## GetChannel
- Description: 입력 인덱스에 해당하는 채널을 얻는다.
- Declaration: `Source/NXVideo/XVideo.h:106`
- Implementation: `Source/NXVideo/XVideo.cpp:178`

## GetChannelProxy
- Description: 입력 인덱스에 해당하는 채널의 프록시를 얻는다.
- Declaration: `Source/NXVideo/XVideo.h:111`
- Implementation: `Source/NXVideo/XVideo.cpp:185`

## GetLastError
- Description: Error가 존재할시 마지막 발생한 Error를 얻는다.
- Declaration: `Source/NXVideo/XVideo.h:61`
- Implementation: `Source/NXVideo/XVideo.cpp:117`

## GetNativeVideo
- Description: 비관리 객체 XVideo 포인터를 얻는다.
- Declaration: `Source/NXVideo/XVideo.h:40`
- Implementation: `not found`

## GetNumChannels
- Description: 객체에 포함된 채널의 수를 얻는다.
- Declaration: `Source/NXVideo/XVideo.h:101`
- Implementation: `Source/NXVideo/XVideo.cpp:171`

## GetNumStreams
- Description: 총 스트림의 수를 얻는다.
- Declaration: `Source/NXVideo/XVideo.h:97`
- Implementation: `Source/NXVideo/XVideo.cpp:164`

## Pause
- Description: 전체 비디오 채널 재생을 일시 정지한다.
- Declaration: `Source/NXVideo/XVideo.h:64`
- Implementation: `Source/NXVideo/XVideo.cpp:130`

## PtsToStreamTime
- Description: 첫 재생 채널 기준 PTS값을 시간으로 변환한다. 입력된 PTS(Presentation Time Stamp)에 대한 시간(초)를 계산한다. 특정 시간에 대한 시간 = (입력 PTS값 - 시작 PTS값) * PTS에 대한 시간 환산 값.
- Declaration: `Source/NXVideo/XVideo.h:93`
- Implementation: `Source/NXVideo/XVideo.cpp:159`

## Resume
- Description: 일시 정지된 비디오 재생을 재개한다.
- Declaration: `Source/NXVideo/XVideo.h:67`
- Implementation: `Source/NXVideo/XVideo.cpp:137`

## Seek
- Description: 비디오 안에서 재생 시작이 가장 빠른 채널을 기준으로 탐색을 수행한다.
- Declaration: `Source/NXVideo/XVideo.h:71`, `Source/NXVideo/XVideo.h:75`
- Implementation: `Source/NXVideo/XVideo.cpp:144`, `Source/NXVideo/XVideo.cpp:149`

## StreamTimeToPts
- Description: 시간을 첫 재생 채널 기준 PTS값으로 변환한다. 입력된 재생 시간에 대한 PTS를 계산한다. 특정 시간에 대한 PTS = 시작 PTS + 입력 시간 * 시간에 대한 PTS 환산 값.
- Declaration: `Source/NXVideo/XVideo.h:84`
- Implementation: `Source/NXVideo/XVideo.cpp:154`
