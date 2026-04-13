---
title: Pixoneer.NXDL.NXVideo.NXVideoTranscodeLayer Methods
aliases:
  - NXVideoTranscodeLayer Methods
  - Pixoneer.NXDL.NXVideo.NXVideoTranscodeLayer
  - NXVideoTranscodeLayer
symbols:
  - NXVideoTranscodeLayer
  - CropFrame
  - PauseTranscoding
  - ResumeTranscoding
  - SetEncoder
  - StartTranscoding
  - StopTranscoding
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
- Type: `NXVideoTranscodeLayer`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_NXVideoTranscodeLayer.htm`
- Type declaration: `Source/NXVideo/NXVideoLayerFunction.h:36`
- Method count: `6`

## CropFrame
- Description: 입력 동영상에서 내보낼 화면 영역을 설정한다. 영역 설정을 하지 않으면 입력 영상 전체를 PRESERVE_RATIO_FULL 모드로 내보낸다.
- Declaration: `Source/NXVideo/NXVideoLayerFunction.h:61`
- Implementation: `Source/NXVideo/NXVideoLayerFunction.cpp:167`

## PauseTranscoding
- Description: 동영상 출력을 잠시 멈춘다.
- Declaration: `Source/NXVideo/NXVideoLayerFunction.h:66`
- Implementation: `Source/NXVideo/NXVideoLayerFunction.cpp:183`

## ResumeTranscoding
- Description: 동영상 출력을 재개한다.
- Declaration: `Source/NXVideo/NXVideoLayerFunction.h:68`
- Implementation: `Source/NXVideo/NXVideoLayerFunction.cpp:188`

## SetEncoder
- Description: 동영상 인코더를 설정한다.
- Declaration: `Source/NXVideo/NXVideoLayerFunction.h:52`
- Implementation: `Source/NXVideo/NXVideoLayerFunction.cpp:56`

## StartTranscoding
- Description: 동영상 출력을 시작한다.
- Declaration: `Source/NXVideo/NXVideoLayerFunction.h:64`
- Implementation: `Source/NXVideo/NXVideoLayerFunction.cpp:178`

## StopTranscoding
- Description: 동영상 출력을 종료한다. 인코더가 종료되므로 다시 동영상 출력을 할 수 없다.
- Declaration: `Source/NXVideo/NXVideoLayerFunction.h:70`
- Implementation: `Source/NXVideo/NXVideoLayerFunction.cpp:193`
