---
title: Pixoneer.NXDL.NXVideo.XUASLocalSetEncoder Methods
aliases:
  - XUASLocalSetEncoder Methods
  - Pixoneer.NXDL.NXVideo.XUASLocalSetEncoder
  - XUASLocalSetEncoder
symbols:
  - XUASLocalSetEncoder
  - EncodePacket
  - Flush
  - SetCornerPoints
  - SetFrameCenterPos
  - SetFrameSensor
  - SetLocalSetPacket
  - SetPacket
  - SetSensorFOV
  - SetSensorPlatform
  - SetTagItem
  - SetTagItemDefined
  - SetTimeStamp
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
- Type: `XUASLocalSetEncoder`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XUASLocalSetEncoder.htm`
- Type declaration: `Source/NXVideo/XUasMetadata.h:1726`
- Method count: `12`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XUASLocalSetEncoder
type_name: XUASLocalSetEncoder
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
## EncodePacket
- Description: 현재까지 설정된 항목들을 KLV(Key-Length-Value) 메타데이터 패킷으로 인코딩한다. 만약 필수 항목인 생성 시각 설정이 안 되었으면 인코딩 시점으로 자동 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1753`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1929`

## Flush
- Description: 현재까지 설정된 항목들을 전부 지운다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1756`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1948`

## SetCornerPoints
- Description: 영상 꼭지점의 지상 위치를 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1834`, `Source/NXVideo/XUasMetadata.h:1842`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2010`, `Source/NXVideo/XUasMetadata.cpp:2019`

## SetFrameCenterPos
- Description: 영상 중심점의 지상 좌표를 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1820`, `Source/NXVideo/XUasMetadata.h:1826`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2000`, `Source/NXVideo/XUasMetadata.cpp:2005`

## SetFrameSensor
- Description: 프레임 센서모델로부터 메타데이터 항목을 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1772`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1964`

## SetLocalSetPacket
- Description: 전체 패킷이 아닌 내장 LS 패킷을 인코딩에 추가 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1894`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2123`

## SetPacket
- Description: 인코딩된 패킷을 새로운 인코딩에 추가 설정한다. 패킷 단위로 갱신할 때 쓰인다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1879`, `Source/NXVideo/XUasMetadata.h:1887`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2109`, `Source/NXVideo/XUasMetadata.cpp:2116`

## SetSensorFOV
- Description: 센서 화각을 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1815`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1995`

## SetSensorPlatform
- Description: NED 기준 플랫폼 자세, 센서 상대 자세, 센서 위치를 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1784`, `Source/NXVideo/XUasMetadata.h:1797`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1974`, `Source/NXVideo/XUasMetadata.cpp:1981`

## SetTagItem
- Description: 메타데이터 태그를 지정하여 해당 항목 데이터를 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1866`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2047`

## SetTagItemDefined
- Description: 메타데이터 태그를 지정하여 표준 문서에 정의된 방식으로 데이터를 인코딩한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1872`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2054`

## SetTimeStamp
- Description: 메타데이터 생성 시각을 설정한다. 이 시각은 메타데이터에 포함된 모든 센서 항목들의 취득 시각이다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1760`, `Source/NXVideo/XUasMetadata.h:1764`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1953`, `Source/NXVideo/XUasMetadata.cpp:1958`
