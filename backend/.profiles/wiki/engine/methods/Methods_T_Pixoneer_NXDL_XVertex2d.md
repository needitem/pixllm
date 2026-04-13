---
title: Pixoneer.NXDL.XVertex2d Methods
aliases:
  - XVertex2d Methods
  - Pixoneer.NXDL.XVertex2d
  - XVertex2d
symbols:
  - XVertex2d
  - dotProduct
  - GetNormalize
  - IsEqual
  - norm
  - norm2
  - Normalize
  - ToXVertex3d
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `XVertex2d`
- HTML source: `html/Methods_T_Pixoneer_NXDL_XVertex2d.htm`
- Type declaration: `Source/NXDL/NXDL.h:1165`
- Method count: `7`

## dotProduct
- Description: 객체 자신과 외부 입력 객체간의 Dot-Product를 수행한다.
- Declaration: `Source/NXDL/NXDL.h:1234`, `Source/NXDL/NXDL.h:1239`
- Implementation: `Source/NXDL/XVertex2d.cpp:89`, `Source/NXDL/XVertex2d.cpp:94`

## GetNormalize
- Description: 이 객체의 값을 노멀라이즈하여 반환한다. 이 객체 값은 변하지 않는다.
- Declaration: `Source/NXDL/NXDL.h:1246`
- Implementation: `Source/NXDL/XVertex2d.cpp:106`

## IsEqual
- Description: 만약 입력 XVertex2d객체와 동일하다면 true를 반환하고 그렇지 않으면 false를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1228`
- Implementation: `Source/NXDL/XVertex2d.cpp:73`

## norm
- Description: 이 객체의 Euclidean Norm을 계산하여 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1250`
- Implementation: `Source/NXDL/XVertex2d.cpp:112`

## norm2
- Description: 이 객체의 Euclidean Norm의 제곱을 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1254`
- Implementation: `Source/NXDL/XVertex2d.cpp:117`

## Normalize
- Description: 이 객체의 값을 노멀라이즈한다. x = x/sqrt(x*x + y*y), y = y/sqrt(x*x + y*y).
- Declaration: `Source/NXDL/NXDL.h:1242`
- Implementation: `Source/NXDL/XVertex2d.cpp:99`

## ToXVertex3d
- Description: Xvertex2d를 Xvertex3d로 변환한다.
- Declaration: `Source/NXDL/NXDL.h:1259`
- Implementation: `Source/NXDL/XVertex2d.cpp:122`
