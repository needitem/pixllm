---
title: Pixoneer.NXDL.NXVideo.XUASDatalinkLocalSetInfo Methods
aliases:
  - XUASDatalinkLocalSetInfo Methods
  - Pixoneer.NXDL.NXVideo.XUASDatalinkLocalSetInfo
  - XUASDatalinkLocalSetInfo
symbols:
  - XUASDatalinkLocalSetInfo
  - GetItemTypeInfo
  - GetNativePtr
  - GetNumericValue
  - GetStringValue
  - GetTagName
  - GetTagStatus
  - GetValue
  - GetValueType
  - IsInteger
  - IsNumeric
  - IsReal
  - IsString
  - IsTimeStamp
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
- Type: `XUASDatalinkLocalSetInfo`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XUASDatalinkLocalSetInfo.htm`
- Type declaration: `Source/NXVideo/XUasMetadata.h:524`
- Method count: `13`

## GetItemTypeInfo
- Description: 유효한 메타데이터 항목에 대하여 자료 형식, 수치 형식의 범위, 단위 등 형식 정보를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:577`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:230`

## GetNativePtr
- Description: 비관리 객체 XUASDatalinkLSInfo 포인터를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:546`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:171`

## GetNumericValue
- Description: 유효한 수치형 메타데이터 항목의 인코딩 데이터로부터 수치 데이터 값을 얻는다. 정수형과 실수형 모두 캐스팅하여 반환하며, 정수형일 때 UInt64 데이터는 반환되는 자료 형식을 보고 캐스팅하여 사용한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:588`, `Source/NXVideo/XUasMetadata.h:599`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:246`, `Source/NXVideo/XUasMetadata.cpp:265`

## GetStringValue
- Description: 유효한 문자열 메타데이터 항목의 인코딩 데이터로부터 문자열 값을 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:608`, `Source/NXVideo/XUasMetadata.h:617`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:283`, `Source/NXVideo/XUasMetadata.cpp:301`

## GetTagName
- Description: 표준 문서에 정의된 태그 이름을 얻는다. eUasTag 열거형에 정의되지 않은 설명(Description)을 얻는 ToString() 메소드와 달리 문서 버전 별 정확한 이름을 반환한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:555`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:186`

## GetTagStatus
- Description: 표준 문서에 정의된 태그 상태를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:562`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:210`

## GetValue
- Description: 메타데이터 인코딩 데이터로부터 자료 형식과 그에 따른 값 객체를 얻는다. 숫자와 문자열이 아닌 경우 바이트 배열로 넘긴다.
- Declaration: `Source/NXVideo/XUasMetadata.h:630`, `Source/NXVideo/XUasMetadata.h:644`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:318`, `Source/NXVideo/XUasMetadata.cpp:331`

## GetValueType
- Description: 메타데이터 항목 값의 자료 형식을 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:569`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:220`

## IsInteger
- Description: 주어진 메타데이터 값 형식이 정수형인지 확인한다. 부호를 구분하지 않고, IMAP 형식은 실수형으로 여긴다.
- Declaration: `Source/NXVideo/XUasMetadata.h:657`, `Source/NXVideo/XUasMetadata.h:698`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:444`, `Source/NXVideo/XUasMetadata.cpp:472`

## IsNumeric
- Description: 주어진 메타데이터 값 형식이 수치형인지 확인한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:651`, `Source/NXVideo/XUasMetadata.h:692`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:438`, `Source/NXVideo/XUasMetadata.cpp:467`

## IsReal
- Description: 주어진 메타데이터 값 형식이 실수형인지 확인한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:663`, `Source/NXVideo/XUasMetadata.h:704`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:450`, `Source/NXVideo/XUasMetadata.cpp:477`

## IsString
- Description: 주어진 메타데이터 값 형식이 문자열인지 확인한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:669`, `Source/NXVideo/XUasMetadata.h:710`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:456`, `Source/NXVideo/XUasMetadata.cpp:482`

## IsTimeStamp
- Description: 메타데이터 항목이 MISB 타임스탬프 데이터인지 확인한다. 1970년 1월 1일 0시(UTC)부터 마이크로 초 단위로 센 64비트 부호 없는 정수형으로 표현된다.
- Declaration: `Source/NXVideo/XUasMetadata.h:676`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:462`
