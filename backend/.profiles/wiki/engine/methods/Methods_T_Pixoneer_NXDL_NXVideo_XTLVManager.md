---
title: Pixoneer.NXDL.NXVideo.XTLVManager Methods
aliases:
  - XTLVManager Methods
  - Pixoneer.NXDL.NXVideo.XTLVManager
  - XTLVManager
symbols:
  - XTLVManager
  - AddInt32
  - AddInt64
  - AddUInt32
  - AddUInt64
  - Clear
  - GetTagID
  - GetTLVCount
  - GetValue
  - MakeTLVGroup
  - ParseTLVData
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nxvideo
---

# Overview
- Namespace: `Pixoneer.NXDL.NXVideo`
- Type: `XTLVManager`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XTLVManager.htm`
- Type declaration: `Source/NXVideo/XTLVManager.h:15`
- Method count: `10`

## AddInt32
- Description: 객체에 Tag-Value쌍을 추가한다.
- Declaration: `Source/NXVideo/XTLVManager.h:58`
- Implementation: `Source/NXVideo/XTLVManager.cpp:94`

## AddInt64
- Description: 객체에 Tag-Value쌍을 추가한다.
- Declaration: `Source/NXVideo/XTLVManager.h:68`
- Implementation: `Source/NXVideo/XTLVManager.cpp:109`

## AddUInt32
- Description: 객체에 Tag-Value쌍을 추가한다.
- Declaration: `Source/NXVideo/XTLVManager.h:63`
- Implementation: `Source/NXVideo/XTLVManager.cpp:102`

## AddUInt64
- Description: 객체에 Tag-Value쌍을 추가한다.
- Declaration: `Source/NXVideo/XTLVManager.h:73`
- Implementation: `Source/NXVideo/XTLVManager.cpp:117`

## Clear
- Description: 객체 내부의 TLV 데이터들을 모두 삭제한다.
- Declaration: `Source/NXVideo/XTLVManager.h:31`
- Implementation: `Source/NXVideo/XTLVManager.cpp:39`

## GetTagID
- Description: 입력된 Index에 해당하는 Key값을 얻는다.
- Declaration: `Source/NXVideo/XTLVManager.h:44`
- Implementation: `Source/NXVideo/XTLVManager.cpp:58`

## GetTLVCount
- Description: TLV 쌍의 갯수를 반환한다.
- Declaration: `Source/NXVideo/XTLVManager.h:39`
- Implementation: `Source/NXVideo/XTLVManager.cpp:53`

## GetValue
- Description: 입력된 Index에 해당하는 Value값을 얻는다.
- Declaration: `Source/NXVideo/XTLVManager.h:49`
- Implementation: `Source/NXVideo/XTLVManager.cpp:63`

## MakeTLVGroup
- Description: 추가된 TLV쌍 배열의 값들을 1개의 Byte 배열로 합하는 과정을 수행한다.
- Declaration: `Source/NXVideo/XTLVManager.h:53`
- Implementation: `Source/NXVideo/XTLVManager.cpp:81`

## ParseTLVData
- Description: 외부 데이터 TLV Byte Array로부터 Parsing을 수행하여 Tag-Value 쌍 구조를 생성하여 Tag를 통해 Value를 얻을수 있도록 한다.
- Declaration: `Source/NXVideo/XTLVManager.h:35`
- Implementation: `Source/NXVideo/XTLVManager.cpp:44`
