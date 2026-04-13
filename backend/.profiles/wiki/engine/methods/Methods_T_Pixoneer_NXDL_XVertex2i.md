---
title: Pixoneer.NXDL.XVertex2i Methods
aliases:
  - XVertex2i Methods
  - Pixoneer.NXDL.XVertex2i
  - XVertex2i
symbols:
  - XVertex2i
  - dotProduct
  - GetNormalize
  - IsEqual
  - norm
  - norm2
  - Normalize
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `XVertex2i`
- HTML source: `html/Methods_T_Pixoneer_NXDL_XVertex2i.htm`
- Type declaration: `Source/NXDL/NXDL.h:1740`
- Method count: `6`

## dotProduct
- Description: 객체 자신과 외부 입력 객체간의 Dot-Product를 수행한다.
- Declaration: `Source/NXDL/NXDL.h:1815`, `Source/NXDL/NXDL.h:1822`
- Implementation: `Source/NXDL/XVertex2i.cpp:89`, `Source/NXDL/XVertex2i.cpp:94`

## GetNormalize
- Description: 이 객체의 노멀라이즈결과를 반환한다. 이 객체 값은 변하지 않는다.
- Declaration: `Source/NXDL/NXDL.h:1831`
- Implementation: `Source/NXDL/XVertex2i.cpp:106`

## IsEqual
- Description: 만약 입력 XVertex2i객체와 동일하다면 true를 반환하고 그렇지 않으면 false를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1846`
- Implementation: `Source/NXDL/XVertex2i.cpp:73`

## norm
- Description: 이 객체의 Euclidean Norm을 계산하여 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1835`
- Implementation: `Source/NXDL/XVertex2i.cpp:112`

## norm2
- Description: 이 객체의 Euclidean Norm의 제곱을 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1839`
- Implementation: `Source/NXDL/XVertex2i.cpp:117`

## Normalize
- Description: XVertex2i객체에 대한 Normalize를 수행. x = x/sqrt(x*x + y*y), y = y/sqrt(x*x + y*y).
- Declaration: `Source/NXDL/NXDL.h:1827`
- Implementation: `Source/NXDL/XVertex2i.cpp:99`
