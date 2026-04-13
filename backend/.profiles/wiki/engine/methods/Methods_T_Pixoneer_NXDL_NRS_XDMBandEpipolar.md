---
title: Pixoneer.NXDL.NRS.XDMBandEpipolar Methods
aliases:
  - XDMBandEpipolar Methods
  - Pixoneer.NXDL.NRS.XDMBandEpipolar
  - XDMBandEpipolar
symbols:
  - XDMBandEpipolar
  - ConvPosA2E
  - ConvPosB2E
  - ConvPosE2A
  - ConvPosE2B
  - GetInputParam
  - GetRPCModelA
  - GetRPCModelB
  - SetInputParam
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nrs
---

# Overview
- Namespace: `Pixoneer.NXDL.NRS`
- Type: `XDMBandEpipolar`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XDMBandEpipolar.htm`
- Type declaration: `Source/NXDLrs/XDMBandEpipolar.h:158`
- Method count: `8`

## ConvPosA2E
- Description: Left 영상점에 대응하는 Epipolar 영상점의 좌표를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandEpipolar.h:201`
- Implementation: `Source/NXDLrs/XDMBandEpipolar.cpp:157`

## ConvPosB2E
- Description: Right 영상점에 대응하는 Epipolar 영상점의 좌표를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandEpipolar.h:206`
- Implementation: `Source/NXDLrs/XDMBandEpipolar.cpp:167`

## ConvPosE2A
- Description: Epipolar 영상점에 대응하는 Left 영상점의 좌표를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandEpipolar.h:190`
- Implementation: `Source/NXDLrs/XDMBandEpipolar.cpp:129`

## ConvPosE2B
- Description: Epipolar 영상점에 대응하는 Right 영상점의 좌표를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandEpipolar.h:196`
- Implementation: `Source/NXDLrs/XDMBandEpipolar.cpp:143`

## GetInputParam
- Description: Epipolar 생성을 위해 설정된 입력 변수를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandEpipolar.h:176`
- Implementation: `Source/NXDLrs/XDMBandEpipolar.cpp:102`

## GetRPCModelA
- Description: 설정된 파라미터들로부터 계산된 Left 영상 RPC모델을 얻는다. 이 함수는 XDMBandEpipolarDEM에서 DEM을 생성하기 위해 사용된다.
- Declaration: `Source/NXDLrs/XDMBandEpipolar.h:180`
- Implementation: `Source/NXDLrs/XDMBandEpipolar.cpp:107`

## GetRPCModelB
- Description: 설정된 파라미터들로부터 계산된 Right 영상 얻는다. 이 함수는 XDMBandEpipolarDEM에서 DEM을 생성하기 위해 사용된다.
- Declaration: `Source/NXDLrs/XDMBandEpipolar.h:184`
- Implementation: `Source/NXDLrs/XDMBandEpipolar.cpp:118`

## SetInputParam
- Description: Epipolar 생성을 위한 입력 변수들을 설정한다.
- Declaration: `Source/NXDLrs/XDMBandEpipolar.h:172`
- Implementation: `Source/NXDLrs/XDMBandEpipolar.cpp:78`
