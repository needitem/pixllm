---
title: Pixoneer.NXDL.NXMilmap.NXMilmapLayerComposites Methods
aliases:
  - NXMilmapLayerComposites Methods
  - Pixoneer.NXDL.NXMilmap.NXMilmapLayerComposites
  - NXMilmapLayerComposites
symbols:
  - NXMilmapLayerComposites
  - AddXDMComposite
  - EnableShaderAlgorithm
  - GenShaderCodeBasso
  - GenShaderCodeCBS
  - GenShaderCodeEdge
  - GenShaderCodeHDR
  - GenShaderCodeNew
  - GetLayerID
  - GetXDMCompManager
  - HitTest
  - Initialize
  - Invalidate
  - SetShaderAlgorithm
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nxmilmap
---

# Overview
- Namespace: `Pixoneer.NXDL.NXMilmap`
- Type: `NXMilmapLayerComposites`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXMilmap_NXMilmapLayerComposites.htm`
- Type declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:99`
- Method count: `13`

## AddXDMComposite
- Description: 이 레이어에 XDMComposite를 추가한다.
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:121`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:57`

## EnableShaderAlgorithm
- Description: GPU를 통한 쉐이더 알고리즘을 활성화할지 비활성화할지 설정한다.
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:134`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:75`

## GenShaderCodeBasso
- Description: Basso 쉐이더 코드를 생성한다.
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:161`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:116`

## GenShaderCodeCBS
- Description: CBS(Contrast Brightness Saturation) 쉐이더 코드를 생성한다.
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:149`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:95`

## GenShaderCodeEdge
- Description: 모서리 탐지 쉐이더 코드를 생성한다.
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:157`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:109`

## GenShaderCodeHDR
- Description: HDR(High Dynamic Range) 쉐이더 코드를 생성한다.
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:153`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:102`

## GenShaderCodeNew
- Description: 초기화와 함께 새로운 쉐이더 코드를 생성한다.
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:145`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:88`

## GetLayerID
- Description: 레이어의 ID를 가져온다. (Overrides NXRenderLayerGetLayerID)
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:116`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:50`

## GetXDMCompManager
- Description: 이 레이어의 composite 관리자를 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:125`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:63`

## HitTest
- Description: 화면에 도시된 XDMComposite 중에서 특정 위치에 Hitting 되는 XDMComposite 중 가장 상위의 XDMComposite 를 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:291`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:123`

## Initialize
- Description: 내부 초기화 함수. 최초로 사용될 때 NXMilmapEngine이 자동호출한다. (Overrides NXRenderLayerInitialize)
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:113`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:41`

## Invalidate
- Description: 설정된 색합성을 반영하여 화면을 갱신하도록 한다.
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:129`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:69`

## SetShaderAlgorithm
- Description: 쉐이더 알고리즘 코드를 설정한다.
- Declaration: `Source/NXMilmap/NXMilmapLayerComposites.h:139`
- Implementation: `Source/NXMilmap/NXMilmapLayerComposites.cpp:81`
