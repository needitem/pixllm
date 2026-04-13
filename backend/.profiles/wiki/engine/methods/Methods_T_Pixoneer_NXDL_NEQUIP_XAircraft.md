---
title: Pixoneer.NXDL.NEQUIP.XAircraft Methods
aliases:
  - XAircraft Methods
  - Pixoneer.NXDL.NEQUIP.XAircraft
  - XAircraft
symbols:
  - XAircraft
  - AddModel
  - LoadModel
  - LoadModelForReloading
  - SetAOA
  - SetDive
  - SetModelOrientation
  - SetRot
  - SetSpeedMach
  - SetSpeedMPS
  - UpdateModel
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nequip
---

# Overview
- Namespace: `Pixoneer.NXDL.NEQUIP`
- Type: `XAircraft`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NEQUIP_XAircraft.htm`
- Type declaration: `Source/NXDLncw/NXDLequip.h:262`
- Method count: `10`

## AddModel
- Description: 파일경로에서 비행체 모델을 로딩하여 모델 목록에 추가한다. 하나 이상의 모델을 이용하여 비행체를 렌더링할 수 있도록 한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:292`
- Implementation: `Source/NXDLncw/XAircraft.cpp:111`

## LoadModel
- Description: 파일경로에서 비행체 모델을 로딩한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:280`, `Source/NXDLncw/NXDLequip.h:286`
- Implementation: `Source/NXDLncw/XAircraft.cpp:84`, `Source/NXDLncw/XAircraft.cpp:89`

## LoadModelForReloading
- Description: 파일경로에서 비행체 모델을 로딩한다. BlendMode 설정에 따라 모델을 도시할 수 있도록 한다. 현재는 3DS 파일만을 지원한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:299`
- Implementation: `Source/NXDLncw/XAircraft.cpp:100`

## SetAOA
- Description: 받음각(Angle of attack. 비행 방향인 공기 흐름의 속도 방향과 날개 시위선이 만드는 사이 각)을 설정한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:310`
- Implementation: `Source/NXDLncw/XAircraft.cpp:139`

## SetDive
- Description: 강하(Dive) 각도를 설정한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:315`
- Implementation: `Source/NXDLncw/XAircraft.cpp:147`

## SetModelOrientation
- Description: 모델 좌표계에서 모델 지향과 상향 벡터를 지정한다. 영벡터가 입력되면 무시한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:304`
- Implementation: `Source/NXDLncw/XAircraft.cpp:130`

## SetRot
- Description: Rate one turn을 설정한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:320`
- Implementation: `Source/NXDLncw/XAircraft.cpp:155`

## SetSpeedMach
- Description: 마하(mach) 속도를 설정한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:325`
- Implementation: `Source/NXDLncw/XAircraft.cpp:163`

## SetSpeedMPS
- Description: Speed on meter per second = mach * 340.3 (sonic speed).
- Declaration: `Source/NXDLncw/NXDLequip.h:331`
- Implementation: `Source/NXDLncw/XAircraft.cpp:170`

## UpdateModel
- Description: 여러 개의 모델 파일을 추가한 경우, 현재 렌더링하는 모델의 다음 파일로 갱신하도록 한다. 목록의 끝인 경우 처음 모델부터 다시 렌더링한다.
- Declaration: `Source/NXDLncw/NXDLequip.h:295`
- Implementation: `Source/NXDLncw/XAircraft.cpp:122`
