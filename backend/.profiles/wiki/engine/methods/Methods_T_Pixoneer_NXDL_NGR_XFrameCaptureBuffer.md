---
title: Pixoneer.NXDL.NGR.XFrameCaptureBuffer Methods
aliases:
  - XFrameCaptureBuffer Methods
  - Pixoneer.NXDL.NGR.XFrameCaptureBuffer
  - XFrameCaptureBuffer
symbols:
  - XFrameCaptureBuffer
  - BeginPixelProcessingMode
  - CallDraw
  - Capture
  - CopyColorTexture
  - CopyGrayscaleTexture
  - EndPixelProcessingMode
  - GetNativeFBO
  - ImageToScreen
  - ImageToWorld
  - LockBuffer
  - Release
  - SaveFrame
  - ScreenToImage
  - SetEffectBlur
  - SetEffectFog
  - SetEffectRain
  - SetEffectSnow
  - SetSize
  - UnlockBuffer
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - ngr
---

# Overview
- Namespace: `Pixoneer.NXDL.NGR`
- Type: `XFrameCaptureBuffer`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NGR_XFrameCaptureBuffer.htm`
- Type declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:29`
- Method count: `19`

## BeginPixelProcessingMode
- Description: 갈무리 버퍼에 독립적으로 렌더링을 하는 모드를 시작한다. 주로 쉐이더를 통한 오프-스크린 픽셀 처리에 쓰인다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:321`
- Implementation: `Source/NXDLgr/XFrameCaptureBuffer.cpp:614`

## CallDraw
- Description: 갈무리한 컬러 영상을 주어진 사각형 안에 그린다. GL 명령을 쓸 수 있도록 렌더링 컨텍스트가 활성화된 상태에서 불러야 한다. XDL 그래픽 아키텍처에서 렌더 콜백 이벤트 등에서 불러쓸 수 있다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:227`
- Implementation: `Source/NXDLgr/XFrameCaptureBuffer.cpp:232`

## Capture
- Description: 갈무리 버퍼 텍스처 데이터를 접근 가능한 메모리로 복사한다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:333`
- Implementation: `Source/NXDLgr/XFrameCaptureBuffer.cpp:604`

## CopyColorTexture
- Description: 갈무리 버퍼의 컬러 텍스처를 얻는다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:234`, `Source/NXDLgr/XFrameCaptureBuffer.h:238`
- Implementation: `Source/NXDLgr/XFrameCaptureBuffer.cpp:260`, `Source/NXDLgr/XFrameCaptureBuffer.cpp:274`

## CopyGrayscaleTexture
- Description: 갈무리 버퍼의 흑백 텍스처를 얻는다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:241`, `Source/NXDLgr/XFrameCaptureBuffer.h:245`
- Implementation: `Source/NXDLgr/XFrameCaptureBuffer.cpp:291`, `Source/NXDLgr/XFrameCaptureBuffer.cpp:305`

## EndPixelProcessingMode
- Description: 갈무리 버퍼의 독립적인 픽셀 처리 모드를 종료한다. 렌더 컨텍스트를 재설정하도록 설정하면 모드 시작 전에 활성화된 컨텍스트로 되돌린다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:324`
- Implementation: `Source/NXDLgr/XFrameCaptureBuffer.cpp:621`

## GetNativeFBO
- Description: XDL FrameCaptureBuffer 네이티브 객체를 얻는다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:129`
- Implementation: `not found`

## ImageToScreen
- Description: 영상 좌표를 화면 좌표로 변환한다. 고정 크기 버퍼인 경우 두 좌표가 다를 수 있고, 가변 크기의 경우는 항상 같다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:199`
- Implementation: `Source/NXDLgr/XFrameCaptureBuffer.cpp:97`

## ImageToWorld
- Description: 영상 좌표를 3차원 모델 좌표로 변환한다. 3차원 좌표를 갈무리하는 경우에만 대응 좌표를 반환한다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:206`
- Implementation: `Source/NXDLgr/XFrameCaptureBuffer.cpp:112`

## LockBuffer
- Description: 갈무리 데이터에 접근할 때 필요시 버퍼를 잠근다. 개별 자료 접근은 동기화되어 있으나 여러 자료에 접근할 때 쓴다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:213`
- Implementation: `not found`

## Release
- Description: 프레임 갈무리 버퍼와 관련된 리소스 및 메모리를 해제한다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:117`, `Source/NXDLgr/XFrameCaptureBuffer.h:121`
- Implementation: `Source/NXDLgr/XFrameCaptureBuffer.h:121`

## SaveFrame
- Description: 갈무리한 프레임을 이미지로 저장한다. RGB 데이터 또는 흑백 영상에 대한 갈무리가 완료된 상태여야 한다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:255`
- Implementation: `Source/NXDLgr/XFrameCaptureBuffer.cpp:322`

## ScreenToImage
- Description: 화면 좌표를 영상 좌표로 변환한다. 고정 크기 버퍼인 경우 두 좌표가 다를 수 있고, 가변 크기의 경우는 항상 같다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:192`
- Implementation: `Source/NXDLgr/XFrameCaptureBuffer.cpp:83`

## SetEffectBlur
- Description: 갈무리 영상을 흐리게 하는 블러(Blur) 효과 적용 여부를 설정한다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:260`
- Implementation: `not found`

## SetEffectFog
- Description: 갈무리 영상에 안개가 낀 효과 적용 여부를 설정한다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:314`
- Implementation: `not found`

## SetEffectRain
- Description: 갈무리 영상에 비가 내리는 효과 적용 여부를 설정한다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:296`
- Implementation: `not found`

## SetEffectSnow
- Description: 갈무리 영상에 눈이 내리는 효과 적용 여부를 설정한다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:278`
- Implementation: `not found`

## SetSize
- Description: 프레임 갈무리 버퍼의 크기를 정한다. 고정 크기로 하면 뷰 화면 크기와 다르게 영상 크기를 지정할 수 있다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:185`
- Implementation: `Source/NXDLgr/XFrameCaptureBuffer.cpp:75`

## UnlockBuffer
- Description: 갈무리 데이터 접근 잠금을 푼다.
- Declaration: `Source/NXDLgr/XFrameCaptureBuffer.h:215`
- Implementation: `not found`
