---
title: Pixoneer.NXDL.Xmt Methods
aliases:
  - Xmt Methods
  - Pixoneer.NXDL.Xmt
  - Xmt
symbols:
  - Xmt
  - Hermite2PVA
  - Hermite4PV
  - Hermite6P
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `Xmt`
- HTML source: `html/Methods_T_Pixoneer_NXDL_Xmt.htm`
- Type declaration: `Source/NXDL/NXDL.h:3084`
- Method count: `3`

## Hermite2PVA
- Description: 두 점의 2차원 위치, 속도, 가속도로부터 허밋 보간을 수행한다.
- Declaration: `Source/NXDL/NXDL.h:3101`, `Source/NXDL/NXDL.h:3116`, `Source/NXDL/NXDL.h:3131`
- Implementation: `Source/NXDL/XHermite.cpp:19`, `Source/NXDL/XHermite.cpp:29`, `Source/NXDL/XHermite.cpp:40`, `Source/NXDL/XHermite.cpp:56`, `Source/NXDL/XHermite.cpp:68`, `Source/NXDL/XHermite.cpp:84`

## Hermite4PV
- Description: 네 점의 2차원 위치, 속도로부터 허밋 보간을 수행한다.
- Declaration: `Source/NXDL/NXDL.h:3142`, `Source/NXDL/NXDL.h:3152`, `Source/NXDL/NXDL.h:3162`
- Implementation: `Source/NXDL/XHermite.cpp:96`, `Source/NXDL/XHermite.cpp:107`, `Source/NXDL/XHermite.cpp:119`, `Source/NXDL/XHermite.cpp:136`, `Source/NXDL/XHermite.cpp:148`, `Source/NXDL/XHermite.cpp:165`

## Hermite6P
- Description: 여섯 점의 2차원 위치로부터 허밋 보간을 수행한다.
- Declaration: `Source/NXDL/NXDL.h:3172`, `Source/NXDL/NXDL.h:3181`, `Source/NXDL/NXDL.h:3190`
- Implementation: `Source/NXDL/XHermite.cpp:177`, `Source/NXDL/XHermite.cpp:189`, `Source/NXDL/XHermite.cpp:201`, `Source/NXDL/XHermite.cpp:217`, `Source/NXDL/XHermite.cpp:229`, `Source/NXDL/XHermite.cpp:246`
