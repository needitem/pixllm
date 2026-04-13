---
title: Pixoneer.NXDL.XMatREAL64 Methods
aliases:
  - XMatREAL64 Methods
  - Pixoneer.NXDL.XMatREAL64
  - XMatREAL64
symbols:
  - XMatREAL64
  - Alloc
  - Copy
  - Free
  - GetAt
  - Identity
  - Inverse
  - InverseL
  - InverseP
  - InverseR
  - SetAt
  - Transpose
  - Zerorize
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `XMatREAL64`
- HTML source: `html/Methods_T_Pixoneer_NXDL_XMatREAL64.htm`
- Type declaration: `Source/NXDL/NXDL.h:2025`
- Method count: `12`

## Alloc
- Description: 행렬의 크기로 배열의 메모리를 할당한다.
- Declaration: `not found`
- Implementation: `Source/NXDL/XMat.cpp:69`, `Source/NXVideo/NXVideoExtension.cpp:15`, `Source/NXVideo/NXVideoExtension.cpp:20`, `Source/NXVideo/NXVideoExtension.cpp:26`

## Copy
- Description: 매개변수 행렬의 값으로 설정한다.
- Declaration: `not found`
- Implementation: `Source/NXDL/XMat.cpp:168`, `Source/NXVideo/NXVideoExtension.cpp:94`, `Source/NXVideo/NXVideoExtension.cpp:102`

## Free
- Description: XMatREAL64 객체의 메모리를 해제한다.
- Declaration: `not found`
- Implementation: `Source/NXDL/XMat.cpp:63`

## GetAt
- Description: 행렬의 원소값을 가져온다.
- Declaration: `not found`
- Implementation: `Source/NXDL/XMat.cpp:175`

## Identity
- Description: 단위행렬로 초기화한다. 정방행렬이 아닌 경우 가능한 대각 요소만 1로 한다.
- Declaration: `not found`
- Implementation: `Source/NXDL/XMat.cpp:87`

## Inverse
- Description: 가우스 소거법을 이용하여 역행렬로 변환한다. (배정도 실수 유효숫자를 고려하여 부정확한 결과가 예상되는 경우 InverseP() 사용을 추천함)
- Declaration: `not found`
- Implementation: `Source/NXDL/XMat.cpp:105`

## InverseL
- Description: 다음과 같이 행렬의 왼쪽에 곱해서 단위행렬이 얻어지는 행렬로 변환한다. Left Inverse: ((AT*A)'*AT)*A = I
- Declaration: `not found`
- Implementation: `Source/NXDL/XMat.cpp:111`

## InverseP
- Description: 특이값 분해(SVD)를 통해 의사 역행렬(Pseudo inverse)로 변환한다.
- Declaration: `not found`
- Implementation: `Source/NXDL/XMat.cpp:123`

## InverseR
- Description: 다음과 같이 행렬의 오른쪽에 곱해서 단위행렬이 얻어지는 행렬로 변환한다. Right Inverse: A*(AT*(A*AT)' = I
- Declaration: `not found`
- Implementation: `Source/NXDL/XMat.cpp:117`

## SetAt
- Description: 행렬의 원소값을 설정한다.
- Declaration: `not found`
- Implementation: `Source/NXDL/XMat.cpp:181`

## Transpose
- Description: 행렬의 행과 열의 요소를 바꾼다.
- Declaration: `not found`
- Implementation: `Source/NXDL/XMat.cpp:99`

## Zerorize
- Description: 행렬의 값을 0으로 초기화한다.
- Declaration: `not found`
- Implementation: `Source/NXDL/XMat.cpp:81`
