---
title: Pixoneer.NXDL.NXVideo.XUASLocalSetDecoder Methods
aliases:
  - XUASLocalSetDecoder Methods
  - Pixoneer.NXDL.NXVideo.XUASLocalSetDecoder
  - XUASLocalSetDecoder
symbols:
  - XUASLocalSetDecoder
  - Decode
  - GetCornerPoint
  - GetFrameCenterPos
  - GetFrameSensor
  - GetNativeDecoder
  - GetNumericValue
  - GetNumericValueKLV
  - GetPlatformAttitude
  - GetSensorAttitude
  - GetSensorFOV
  - GetSensorPosition
  - GetStringValue
  - GetTimeStamp
  - GetValue
  - GetValueInfo
  - HasTagItem
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
- Type: `XUASLocalSetDecoder`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XUASLocalSetDecoder.htm`
- Type declaration: `Source/NXVideo/XUasMetadata.h:1432`
- Method count: `16`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XUASLocalSetDecoder
type_name: XUASLocalSetDecoder
namespace: Pixoneer.NXDL.NXVideo
method_section_prefix: "## "
verification_rules:
  - treat_declaration_lines_as_symbol_existence_evidence
  - treat_implementation_lines_as_source_anchor_evidence
  - prefer_this_page_over_examples_for_exact_call_shapes
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page to verify exact symbol existence before emitting code.
- Cross-check declaration and implementation lines when overloads or call shapes matter.
- Treat examples and workflow pages as composition guidance, but treat this page as the canonical member list.
## Decode
- Description: KLV(Key-Length-Value) 메타데이터 패킷을 디코딩하고 태그 항목별 값 목록을 만든다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1500`, `Source/NXVideo/XUasMetadata.h:1506`, `Source/NXVideo/XUasMetadata.h:1514`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1484`, `Source/NXVideo/XUasMetadata.cpp:1499`, `Source/NXVideo/XUasMetadata.cpp:1519`

## GetCornerPoint
- Description: 영상 꼭지점의 지상 위치를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1563`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1634`

## GetFrameCenterPos
- Description: 영상 중심점의 지상 위치를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1551`, `Source/NXVideo/XUasMetadata.h:1557`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1594`, `Source/NXVideo/XUasMetadata.cpp:1613`

## GetFrameSensor
- Description: 메타데이터로부터 프레임 센서모델을 생성한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1570`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1652`

## GetNativeDecoder
- Description: XDL 내부 비관리 디코더 포인터를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1710`
- Implementation: `not found`

## GetNumericValue
- Description: 메타데이터 태그 항목이 수치 데이터일 때 디코딩 값을 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1608`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1733`

## GetNumericValueKLV
- Description: 메타데이터 태그 항목의 인코딩 데이터를 빅-엔디안 정수로 읽은 값을 얻는다. 실제 인코딩 형식과 무관하게 인코딩 데이터 길이가 충분하면 정수형으로 바꿔 반환한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1650`, `Source/NXVideo/XUasMetadata.h:1658`, `Source/NXVideo/XUasMetadata.h:1666`, `Source/NXVideo/XUasMetadata.h:1674`, `Source/NXVideo/XUasMetadata.h:1682`, `Source/NXVideo/XUasMetadata.h:1690`, `Source/NXVideo/XUasMetadata.h:1698`, `Source/NXVideo/XUasMetadata.h:1706`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1792`, `Source/NXVideo/XUasMetadata.cpp:1800`, `Source/NXVideo/XUasMetadata.cpp:1808`, `Source/NXVideo/XUasMetadata.cpp:1816`, `Source/NXVideo/XUasMetadata.cpp:1824`, `Source/NXVideo/XUasMetadata.cpp:1832`, `Source/NXVideo/XUasMetadata.cpp:1840`, `Source/NXVideo/XUasMetadata.cpp:1848`

## GetPlatformAttitude
- Description: NED 좌표계 기준 플랫폼(비행체)의 자세를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1546`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1581`

## GetSensorAttitude
- Description: 센서의 상대적 자세를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1539`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1568`

## GetSensorFOV
- Description: 센서의 가로, 세로 화각을 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1521`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1539`

## GetSensorPosition
- Description: 센서의 위치를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1526`, `Source/NXVideo/XUasMetadata.h:1532`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1547`, `Source/NXVideo/XUasMetadata.cpp:1555`

## GetStringValue
- Description: 메타데이터 태그 항목이 문자열일 때 디코딩 값을 얻는다. 인코딩 데이터가 UTF-8 텍스트로 가정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1616`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1748`

## GetTimeStamp
- Description: 메타데이터가 생성된 시각을 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1575`, `Source/NXVideo/XUasMetadata.h:1580`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1660`, `Source/NXVideo/XUasMetadata.cpp:1668`

## GetValue
- Description: 메타데이터 태그를 지정하여 해당 항목의 디코딩 데이터를 얻는다. 메타데이터 항목 형식에 따라 정수형 계열, 실수형의 수치 데이터, 문자열, 날짜와 시간, 바이트 배열 객체로 반환된다. 정수형 계열은 정의된 비트 수의 자료형으로 하되 가변 길이 정수와 식별자는 64비트 자료형으로 반환한다. 실수형 데이터는 Double형 객체로 반환하고, 문자열은 String 객체로 반환한다. 타임스탬프는 이 메서드에서만 System.DateTime 형식으로 바꿔서 반환한다. 다른 데이터 자료형은 인코딩 데이터를 복사한 바이트 배열로 반환한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1598`, `Source/NXVideo/XUasMetadata.h:1628`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1714`, `Source/NXVideo/XUasMetadata.cpp:1761`

## GetValueInfo
- Description: 메타데이터 태그 항목의 디코딩 값과 형식 정보를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1641`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1775`

## HasTagItem
- Description: 메타데이터 태그 항목을 포함하고 있는지 확인한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1592`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1709`
