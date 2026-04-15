---
title: Pixoneer.NXDL.NXVideo.XVideoChannel Methods
aliases:
  - XVideoChannel Methods
  - Pixoneer.NXDL.NXVideo.XVideoChannel
  - XVideoChannel
symbols:
  - XVideoChannel
  - Activate
  - AddVideoFrameFilter
  - AnalyzeBackward
  - AnalyzeForward
  - ClearFrameBuffer
  - CloseOutputUrl
  - DateTimeToTimeStamp
  - Deactivate
  - EnableBackwardAnalysis
  - FrameNumberToPts
  - GetBitRateVideo
  - GetDuration
  - GetFirstDataPts
  - GetFirstPts
  - GetFrameRateMetad
  - GetFrameRateVideo
  - GetLastPts
  - GetNativeChannel
  - GetNumFramesVideo
  - GetPacketQueueSizeMetad
  - GetPacketQueueSizeVideo
  - GetRenderedFrame
  - GetRenderedFrameRGB
  - GetRenderedMetadFrame
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
- Type: `XVideoChannel`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XVideoChannel.htm`
- Type declaration: `Source/NXVideo/XVideoChannel.h:28`
- Method count: `54`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XVideoChannel
type_name: XVideoChannel
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
## Activate
- Description: XVideo객체에 포함된 XVideoChannel객체 중 이 객체를 활성화한다. 활성화된 객체만 스트리밍이 수행된다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:372`

## AddVideoFrameFilter
- Description: 영상 프레임 처리 필터를 추가한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:795`

## AnalyzeBackward
- Description: 뒤로 한 프레임씩 분석하기 위해 현 재생위치에서 직전 프레임을 재생하고 멈춘다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:456`, `Source/NXVideo/XVideoChannel.cpp:466`

## AnalyzeForward
- Description: 앞으로 한 프레임씩 분석하기 위해 현 재생위치에서 다음 프레임을 재생하고 멈춘다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:451`, `Source/NXVideo/XVideoChannel.cpp:461`

## ClearFrameBuffer
- Description: Frame Buffer를 삭제한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:919`

## CloseOutputUrl
- Description: 비디오 채널 녹화 또는 전송을 마무리한다. 파일로 저장하는 경우 필요한 정보들을 추가로 기록하고 파일을 닫는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:1124`

## DateTimeToTimeStamp
- Description: DateTime을 MISB ST 타임스탬프로 변환한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1960`, `Source/NXVideo/XVideoChannel.cpp:693`

## Deactivate
- Description: 활성화된 객체를 비활성화시킨다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:378`

## EnableBackwardAnalysis
- Description: 뒤로 한 프레임씩 분석하는 기능을 활성화한다. 128장의 프레임을 기억하는데, 영상 크기에 따라 메모리를 많이 차지하므로 기본값은 비활성화 상태이다. 활성화 여부
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:471`

## FrameNumberToPts
- Description: 입력된 Frame Number에 해당하는 PTS를 계산한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:546`

## GetBitRateVideo
- Description: 네트워크로 데이터를 수신 받을시 네트워크 수신율(BitRate : 초당 수신 bit수)를 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:504`

## GetDuration
- Description: Video의 Play할 시간(Sec)을 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:476`

## GetFirstDataPts
- Description: 첫번째 데이터 프레임의 PTS를 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:678`

## GetFirstPts
- Description: 첫번째 영상 프레임의 PTS를 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:511`

## GetFrameRateMetad
- Description: Meta data Frame Rate를 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:490`

## GetFrameRateVideo
- Description: Video Frame Rate를 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:483`

## GetLastPts
- Description: 마지막 영상 프레임의 PTS를 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:518`

## GetNativeChannel
- Description: XDL 내부 비관리 객체 XVideoChannel 포인터를 얻는다.
- Declaration: `not found`
- Implementation: `not found`

## GetNumFramesVideo
- Description: 총 Frame의 수를 얻는다. 프레임 분석을 수행하지 않을 경우 대략적인 값이므로 실제 프레임 개수와 다를 수 있다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:497`

## GetPacketQueueSizeMetad
- Description: Video Frame 영상에 대한 Queue에 쌓여 있는 Packet 큐 크기를 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:574`

## GetPacketQueueSizeVideo
- Description: Video Frame 영상에 대한 Queue에 쌓여 있는 Packet의 크기를 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:567`

## GetRenderedFrame
- Description: 이 함수를 부르는 시점에 도시된 영상을 원본 형식(yuv420p 등)으로 담고 있는 XFramePicture 객체를 생성하여 반환한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:924`, `Source/NXVideo/XVideoChannel.cpp:940`

## GetRenderedFrameRGB
- Description: 이 함수를 부르는 시점에 도시된 영상을 RGB 형식으로 담고 있는 XFramePicture 객체를 생성하여 반환한다. 색 변환을 CPU 병렬 쓰레드로 처리하므로 자원 소모를 고려해야 한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:954`, `Source/NXVideo/XVideoChannel.cpp:999`

## GetRenderedMetadFrame
- Description: 현재 도시된 영상에 대응하는 메타데이터 프레임을 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:641`, `Source/NXVideo/XVideoChannel.cpp:657`

## GetSensorExtrinsicParams
- Description: 입력된 PTS에 해당하는 외부표정요소를 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:619`

## GetSensorIntrinsicParams
- Description: 입력된 PTS에 해당하는 내부표정요소를 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:588`

## GetSpeed
- Description: 비디오 Play의 속도(배속)를 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:560`

## GetStartTime
- Description: 첫번째 영상 프레임의 기록 시각을 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:701`

## GetStartTimeStamp
- Description: 첫번째 영상 프레임의 기록 시각을 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:715`

## IsActivated
- Description: 이 객체가 활성화되었는지 여부를 확인한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:384`

## IsPaused
- Description: 비디오 채널이 멈춰있는 상태인지 재생 중인지를 확인한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:403`

## IsStopped
- Description: 비디오 채널이 중지된 상태인지 확인한다. 일시정지와 달리 중지된 경우, 다시 재생할 때 처음부터 재생된다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:423`

## OpenOutputProgram
- Description: 비디오 채널을 재생하면서 동시에 MPEG-TS 형식의 프로그램으로 저장하거나 스트리밍을 하도록 준비한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:1106`, `Source/NXVideo/XVideoChannel.cpp:1115`

## OpenOutputUrl
- Description: 비디오 채널을 재생하면서 동시에 MPEG-TS 형식의 파일로 저장하거나 스트리밍을 하도록 준비한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:1092`, `Source/NXVideo/XVideoChannel.cpp:1099`

## Pause
- Description: Video를 잠시 멈춤을 설정한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:409`

## Play
- Description: Video Channel을 처음부터 재생하도록 Play 신호를 설정한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:390`

## PlayAlong
- Description: Video Channel을 현재 재생 중인 프로그램 또는 다른 채널의 시간에 맞추어 재생하도록 설정한다. 만약 현재 재생 시각을 알 수 없다면 처음부터 재생한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:397`

## PtsToFrameNumber
- Description: PTS값을 입력하여 Frame Number를 계산한다. Frame Number = 시작입력 PTS로부터 계산된 시간 * 초당 Frame 수.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:539`

## PtsToRecordTime
- Description: 프레임 PTS에 대응하는 기록 시각을 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:737`

## PtsToRecordTimeStamp
- Description: 프레임 PTS에 대응하는 기록 시각을 마이크로초 단위 유닉스(UNIX) 시간으로 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:751`

## PtsToStreamTime
- Description: PTS값을 시간으로 변환한다. 입력된 PTS(Presentation Time Stamp)에 대한 시간(초)를 계산한다. 특정 시간에 대한 시간 = (입력 PTS값 - 시작 PTS값) * PTS에 대한 시간 환산 값.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:532`

## RecordTimeToPts
- Description: 기록 시각에 해당하는 프레임 PTS를 얻는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:720`, `Source/NXVideo/XVideoChannel.cpp:732`

## RemoveVideoFrameFilter
- Description: 영상 프레임 처리 필터를 제거한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:805`

## ResetMetad
- Description: 이 함수를 부르는 시점에 도시된 영상을 RGB 형식으로 담고 있는 XFramePicture 객체를 생성하여 반환한다. 색 변환을 CPU 병렬 쓰레드로 처리하므로 자원 소모를 고려해야 한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:671`

## Resume
- Description: Video에 설정된 잠시 멈춤을 다시 시작을 설정한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:416`

## Seek
- Description: 동영상 파일의 경우 시간을 통해 Play할 위치를 찾는다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:437`, `Source/NXVideo/XVideoChannel.cpp:444`

## SetSensorExtrinsicParams
- Description: 입력된 PTS에 해당하는 외부표정요소를 설정한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:609`

## SetSensorIntrinsicParams
- Description: 특정 PTS에 대한 센서 내부 표정요소 파라미터를 설정한다. 동영상은 Frame마다 내부 표정요소가 변경될수 있기 대문에 PTS에 대한 내부 표정요소를 VideoChannel에 설정한다. 센서 내부 표정요소는 동영상에 대한 센서모델을 통해 동영상의 이미지 좌표에 대한 지리좌표를 계산하거나 지리좌표에 대한 이미지 좌표를 계산이 가능한다. 보통 PTS에 대한 센서 내부 표정요소는 Metadata Event를 통해 전달되며 Parsing을 통해 내부 표정요소들을 정의할 수 있다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:581`

## SetSpeed
- Description: 비디오 Play의 속도를 증가시키기 위해 Speed값을 설정한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:553`

## StartTranscoding
- Description: 비디오 채널 녹화 또는 전송을 시작한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:1130`

## Stop
- Description: Play되는 Video를 멈춘다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:430`

## StopTranscoding
- Description: 비디오 채널 녹화 또는 전송을 중지한다. 이 경우, 비디오 출력만 멈추고, 만약 파일로 저장하는 경우 CloseOutputUrl() 메쏘드를 불러야 파일 저장이 완료된다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:1136`

## StreamTimeToPts
- Description: 시간을 PTS값으로 변환한다. 입력된 Play 시간에 대한 PTS를 계산한다. 특정 시간에 대한 PTS = 시작 PTS + 입력 시간 * 시간에대한 PTS 환산 값.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:525`

## TimeStampToDateTime
- Description: MISB ST 타임스탬프를 DateTime으로 변환한다.
- Declaration: `not found`
- Implementation: `Source/NXVideo/XFramePicture.cpp:611`, `Source/NXVideo/XUasMetadata.cpp:360`, `Source/NXVideo/XUasMetadata.cpp:1674`, `Source/NXVideo/XVideoChannel.cpp:683`
