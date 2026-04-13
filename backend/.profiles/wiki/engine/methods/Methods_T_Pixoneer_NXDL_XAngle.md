---
title: Pixoneer.NXDL.XAngle Methods
aliases:
  - XAngle Methods
  - Pixoneer.NXDL.XAngle
  - XAngle
symbols:
  - XAngle
  - Abs
  - FromDegree
  - FromDms
  - FromRadian
  - GetDms
  - GetDmsString
  - IsEqual
  - IsNaN
  - Normalize
  - SetDms
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `XAngle`
- HTML source: `html/Methods_T_Pixoneer_NXDL_XAngle.htm`
- Type declaration: `Source/NXDL/NXDL.h:918`
- Method count: `10`

## Abs
- Description: Static 함수로, XAngle값을 입력 받아 절대값 XAngle 객체를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1002`
- Implementation: `Source/NXDL/XAngle.cpp:93`

## FromDegree
- Description: Static 함수로, Degree값을 입력 받아 새로운 XAngle 객체를 생성한다.
- Declaration: `Source/NXDL/NXDL.h:986`
- Implementation: `Source/NXDL/NXDL.cpp:1228`, `Source/NXDL/NXDL.cpp:1236`, `Source/NXDL/XAngle.cpp:79`, `Source/NXDLMilSymbol/reference/DrawOverItem.cpp:102`, `Source/NXDLMilSymbol/reference/DrawOverItem.cpp:103`, `Source/NXDLMilSymbol/reference/DrawOverItem.cpp:104`, `Source/NXDLMilSymbol/reference/DrawOverItem.cpp:105`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3035`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3036`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3037`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3038`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3786`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3787`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3985`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3986`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4000`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4001`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4045`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4046`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4071`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4072`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4073`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4074`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4075`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4076`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4144`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4145`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4170`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4171`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4172`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4173`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4174`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4175`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4176`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4177`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4296`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4297`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4333`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4334`, `Source/NXDLrs/XDMBand.cpp:224`, `Source/NXDLrs/XDMBandSuperClass.cpp:107`, `Source/NXDLrs/XDMBandTopoModel.cpp:29`, `Source/NXDLrs/XDMBandTopoModel.cpp:30`, `Source/NXDLrs/XDMBandTopoModel.cpp:40`, `Source/NXDLrs/XDMBandTopoModel.cpp:41`, `Source/NXDLsar/XSatellite.cpp:46`, `Source/NXDLsar/XSatellite.cpp:47`, `Source/NXDLsar/XSatellite.cpp:48`, `Source/NXDLscene/XscSymbol.cpp:395`, `Source/NXDLscene/XscSymbol.cpp:403`, `Source/NXPlanet/NXPlanetView.cpp:1551`, `Source/NXVideo/XFrameMetad.cpp:258`, `Source/NXVideo/XFrameMetad.cpp:263`, `Source/NXVideo/XFrameMetad.cpp:268`, `Source/NXVideo/XFrameMetad.cpp:273`, `Source/NXVideo/XFrameMetad.cpp:278`, `Source/NXVideo/XFrameMetad.cpp:288`, `Source/NXVideo/XFrameMetad.cpp:293`, `Source/NXVideo/XFrameMetad.cpp:298`, `Source/NXVideo/XVideoEncoder.cpp:825`, `Source/NXVideo/XVideoEncoder.cpp:858`, `Source/NXVideo/XVideoEncoder.cpp:859`, `Source/NXVideo/XVideoEncoder.cpp:860`, `Source/NXDLMilSymbol/Dependency/include/ICOPS_Framework/ICOPS_struct.h:296`, `Source/NXDLMilSymbol/Dependency/include/ICOPS_Framework/ICOPS_struct.h:301`

## FromDms
- Description: Static 함수로, Degree-Minute-Second값을 입력 받아 새로운 XAngle 객체를 생성한다.
- Declaration: `Source/NXDL/NXDL.h:995`
- Implementation: `Source/NXDL/XAngle.cpp:86`

## FromRadian
- Description: Static 함수로, Radian값을 입력 받아 새로운 XAngle 객체를 생성한다.
- Declaration: `Source/NXDL/NXDL.h:979`
- Implementation: `Source/NXDL/NXDL.cpp:1368`, `Source/NXDL/NXDL.cpp:1369`, `Source/NXDL/NXDL.cpp:1370`, `Source/NXDL/XAngle.cpp:74`, `Source/NXDL/XGeoPoint.cpp:53`, `Source/NXDL/XGeoPoint.cpp:54`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:509`, `Source/NXDLncw/XEquipObj.cpp:281`, `Source/NXMilmap/NXMilmapDrawArgs.cpp:228`, `Source/NXVideo/XFramePicture.cpp:619`, `Source/NXVideo/XVideoEncoder.cpp:821`, `Source/NXVideo/XVideoEncoder.cpp:822`, `Source/NXVideo/XVideoEncoder.cpp:823`, `Source/NXVideo/XVideoEncoder.cpp:840`, `Source/NXVideo/XVideoEncoder.cpp:841`

## GetDms
- Description: Degree-Minute-Second로 Angle값을 반환 한다.
- Declaration: `Source/NXDL/NXDL.h:961`
- Implementation: `Source/NXDL/XAngle.cpp:34`

## GetDmsString
- Description: Degree-Minute-Second 값으로 반환하되 이를 String으로 변환하여 반환한다.
- Declaration: `Source/NXDL/NXDL.h:967`
- Implementation: `Source/NXDL/XAngle.cpp:45`

## IsEqual
- Description: 입력되는 XAngle객체와 동일한 경우 true를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1124`
- Implementation: `Source/NXDL/XAngle.cpp:173`

## IsNaN
- Description: 만약 입력되는 XAngle객체가 NaN이라면 true를 반환하고 그렇지 않으면 false를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1130`
- Implementation: `Source/NXDL/XAngle.cpp:184`

## Normalize
- Description: 내부 Angle값을 0~360도 사이에 존재하도록 Normalize를 수행한다. 예를 들어 375도의 경우 360도가 넘기 때문에 15도가 된다.
- Declaration: `Source/NXDL/NXDL.h:972`
- Implementation: `Source/NXDL/XAngle.cpp:58`

## SetDms
- Description: Degree-Minute-Second 값으로 Angle값을 설정한다.
- Declaration: `Source/NXDL/NXDL.h:953`
- Implementation: `Source/NXDL/XAngle.cpp:66`
