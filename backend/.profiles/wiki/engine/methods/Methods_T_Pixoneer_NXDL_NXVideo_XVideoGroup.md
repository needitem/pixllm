---
title: Pixoneer.NXDL.NXVideo.XVideoGroup Methods
aliases:
  - XVideoGroup Methods
  - Pixoneer.NXDL.NXVideo.XVideoGroup
  - XVideoGroup
symbols:
  - XVideoGroup
  - Clear
  - CloseOutputUrl
  - Dispose
  - GetRecordTimestamp
  - GetRefPts
  - GetRefStreamTime
  - OpenOutputUrl
  - Pause
  - Resume
  - SetGroupMetadAddHandler
  - SetGroupMetadUpdateHandler
  - SetVideoChannels
  - StartMuxing
  - StopMuxing
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
- Type: `XVideoGroup`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XVideoGroup.htm`
- Type declaration: `Source/NXVideo/XVideoGroup.h:18`
- Method count: `14`

## Clear
- Description: 동영상 그룹 구성 채널을 모두 제거한다.
- Declaration: `Source/NXVideo/XVideoGroup.h:61`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:94`

## CloseOutputUrl
- Description: 동영상 그룹 녹화 또는 전송을 마무리한다. 파일로 저장하는 경우 필요한 정보들을 추가로 기록하고 파일을 닫는다.
- Declaration: `Source/NXVideo/XVideoGroup.h:110`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:195`

## Dispose
- Description: 동영상 그룹 소멸자.
- Declaration: `not found`
- Implementation: `not found`

## GetRecordTimestamp
- Description: 채널 PTS에 대응하는 메타데이터 기록 타임스탬프를 구한다.
- Declaration: `Source/NXVideo/XVideoGroup.h:88`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:140`

## GetRefPts
- Description: 채널 PTS에 대응하는 기준 채널 PTS를 구한다.
- Declaration: `Source/NXVideo/XVideoGroup.h:76`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:118`

## GetRefStreamTime
- Description: 채널 PTS에 대응하는 기준 채널 재생 시간을 구한다.
- Declaration: `Source/NXVideo/XVideoGroup.h:82`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:129`

## OpenOutputUrl
- Description: 동영상 그룹을 동기화 재생하면서 동시에 다중 프로그램 MPEG-TS 형식으로 저장하거나 스트리밍을 하도록 준비한다.
- Declaration: `Source/NXVideo/XVideoGroup.h:97`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:151`

## Pause
- Description: 동영상 그룹의 동기화 재생을 멈춘다.
- Declaration: `Source/NXVideo/XVideoGroup.h:66`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:106`

## Resume
- Description: 동영상 그룹의 동기화 재생을 재개한다.
- Declaration: `Source/NXVideo/XVideoGroup.h:64`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:101`

## SetGroupMetadAddHandler
- Description: 동영상 그룹 메타데이터 추가 처리기 설정.
- Declaration: `Source/NXVideo/XVideoGroup.h:114`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:203`

## SetGroupMetadUpdateHandler
- Description: 동영상 그룹 메타데이터 갱신 처리기 설정.
- Declaration: `Source/NXVideo/XVideoGroup.h:117`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:219`

## SetVideoChannels
- Description: No description in HTML reference.
- Declaration: `Source/NXVideo/XVideoGroup.h:53`, `Source/NXVideo/XVideoGroup.h:58`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:43`, `Source/NXVideo/XVideoGroup.cpp:70`

## StartMuxing
- Description: 동기화된 동영상 그룹을 녹화 또는 전송을 시작한다.
- Declaration: `Source/NXVideo/XVideoGroup.h:102`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:175`

## StopMuxing
- Description: 동영상 그룹 녹화 또는 전송을 중지한다. 이 경우, 비디오 출력만 멈추고, 만약 파일로 저장하는 경우 CloseOutputUrl() 메쏘드를 불러야 파일 저장이 완료된다.
- Declaration: `Source/NXVideo/XVideoGroup.h:107`
- Implementation: `Source/NXVideo/XVideoGroup.cpp:185`
