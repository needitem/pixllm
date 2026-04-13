---
title: Pixoneer.NXDL.NXPlanet.NXPlanetLayerComposites Methods
aliases:
  - NXPlanetLayerComposites Methods
  - Pixoneer.NXDL.NXPlanet.NXPlanetLayerComposites
  - NXPlanetLayerComposites
symbols:
  - NXPlanetLayerComposites
  - EnableShaderAlgorithm
  - GenShaderCodeAverage
  - GenShaderCodeBasso
  - GenShaderCodeCBS
  - GenShaderCodeEdge
  - GenShaderCodeHDR
  - GenShaderCodeMedian
  - GenShaderCodeNew
  - GetCartoonEffect
  - GetFilterSize
  - GetFilterType
  - GetLayerID
  - GetShaderCBS
  - GetShaderGamma
  - GetXDMCompManager
  - HitTest
  - Initialize
  - Invalidate
  - Lock
  - ReadPixelValues
  - SetCartoonEffect
  - SetFilterSize
  - SetFilterType
  - SetShaderAlgorithm
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nxplanet
---

# Overview
- Namespace: `Pixoneer.NXDL.NXPlanet`
- Type: `NXPlanetLayerComposites`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXPlanet_NXPlanetLayerComposites.htm`
- Type declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:26`
- Method count: `32`

## EnableShaderAlgorithm
- Description: 쉐이더 알고리즘을 적용할지를 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:70`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:95`

## GenShaderCodeAverage
- Description: Average 필터를 위한 기본 쉐이더 코드를 생성한다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:168`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:284`

## GenShaderCodeBasso
- Description: Basso(Basso-rilievo(BAS-RELIEF) 필터를 위한 기본 쉐이더 코드를 생성한다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:144`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:271`

## GenShaderCodeCBS
- Description: 화면 향상을 위한 대비, 채도, 명도값을 조절 쉐이더 코드를 문자열을 생성한다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:88`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:232`

## GenShaderCodeEdge
- Description: Edge 필터를 위한 기본 쉐이더 코드를 생성한다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:120`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:258`

## GenShaderCodeHDR
- Description: HDR 필터를 위한 기본 쉐이더 코드를 생성한다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:96`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:245`

## GenShaderCodeMedian
- Description: Median 필터를 위한 기본 쉐이더 코드를 생성한다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:192`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:297`

## GenShaderCodeNew
- Description: 기본 쉐이더 코드를 가져온다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:80`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:221`

## GetCartoonEffect
- Description: cartoonEffect 값을 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:265`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:214`

## GetFilterSize
- Description: 필터 크기를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:201`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:122`

## GetFilterType
- Description: 필터 종류를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:227`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:153`

## GetLayerID
- Description: 레이어의 고유 ID를 가져온다.(Overrides NXRenderLayerGetLayerID)
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:44`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:70`

## GetShaderCBS
- Description: 대비, 명도, 채도값을 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:240`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:169`

## GetShaderGamma
- Description: Gamma 값을 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:249`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:186`

## GetXDMCompManager
- Description: XDMCompManager 객체를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:48`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:46`

## HitTest
- Description: 화면에 도시된 XDMComposite 중에서 특정 위치에 Hitting 되는 가장 상위의 XDMComposite 를 가져온다.(Planet2D 모드에서만 가능하다.)
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:430`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:362`

## Initialize
- Description: 내부 초기화 함수 (Overrides NXRenderLayerInitialize)
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:41`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:61`

## Invalidate
- Description: 색합성 정보를 갱신하도록 하며, 컨트롤의 내용을 다시 그리도록 한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:64`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:88`

## Lock
- Description: XDMComposite 객체 추가/삭제/수정 등을 위해 레이어 동작을 제한한다
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:57`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:76`

## ReadPixelValues
- Description: 화면에 도시된 데이터에서 화면 좌표값 기준 픽셀 화소값을 읽어 반환한다. 화소값이 없는 경우 XDataRange.MAX_REAL64 값이 반환된다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:288`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:346`

## SetCartoonEffect
- Description: Edge 필터의 CartoonEffect 값을 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:261`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:207`

## SetFilterSize
- Description: 필터 크기를 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:197`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:114`

## SetFilterType
- Description: 필터 종류를 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:223`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:130`

## SetShaderAlgorithm
- Description: 사용자가 정의하는 쉐이더 알고리즘 문자열을 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:75`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:103`

## SetShaderCBS
- Description: 대비, 명도, 채도값을 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:234`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:161`

## SetShaderGamma
- Description: Gamma 값을 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:245`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:179`

## SetShaderHDR
- Description: HDR Shader 적용 여부를 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:253`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:193`

## SetShaderInvert
- Description: Invert Shader 적용 여부를 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:257`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:200`

## SetXDMCompManager
- Description: XDMCompManager 객체를 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:54`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:53`

## UnLock
- Description: 레이어 동작 제한을 해제한다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:60`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:82`

## ZoomFit
- Description: 화면에 전체 영상이 도시되도록 확대축소하는 함수이다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:269`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:334`

## ZoomFitRect
- Description: 화면에 특정 영역 전체 영상이 도시되도록 확대축소하는 함수이다.
- Declaration: `Source/NXPlanet/NXPlanetLayerComposites.h:277`
- Implementation: `Source/NXPlanet/NXPlanetLayerComposites.cpp:340`
