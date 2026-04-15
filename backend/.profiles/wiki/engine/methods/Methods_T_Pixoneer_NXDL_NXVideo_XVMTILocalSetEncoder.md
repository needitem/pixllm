---
title: Pixoneer.NXDL.NXVideo.XVMTILocalSetEncoder Methods
aliases:
  - XVMTILocalSetEncoder Methods
  - Pixoneer.NXDL.NXVideo.XVMTILocalSetEncoder
  - XVMTILocalSetEncoder
symbols:
  - XVMTILocalSetEncoder
  - Dispose
  - EncodePacket
  - Flush
  - SetFrameCenter
  - SetFrameSize
  - SetLocalSetPacket
  - SetOntologySeries
  - SetTargetSeries
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
- Type: `XVMTILocalSetEncoder`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XVMTILocalSetEncoder.htm`
- Type declaration: `Source/NXVideo/XUasMetadata.h:2350`
- Method count: `9`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XVMTILocalSetEncoder
type_name: XVMTILocalSetEncoder
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
## Dispose
- Description: 소멸자. 즉시 종료자를 부른다.
- Declaration: `not found`
- Implementation: `not found`

## EncodePacket
- Description: 설정 항목들로 구성된 VMTI LS의 인코딩 결과를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:2404`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2726`

## Flush
- Description: 인코더의 내부 데이터를 버리고 인코더를 초기화한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:2406`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2745`

## SetFrameCenter
- Description: 표적 객체 위치의 기준이 되는 영상 프레임 중심점의 지리좌표를 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:2384`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2760`

## SetFrameSize
- Description: 표적 객체 화소 위치의 기준이 되는 대상 영상 프레임의 크기를 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:2377`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2755`

## SetLocalSetPacket
- Description: 전체 패킷이 아닌 내장 LS 패킷을 인코딩에 추가 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:2413`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2792`

## SetOntologySeries
- Description: 메타데이터에 포함할 온톨로지 목록을 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:2389`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2765`

## SetTargetSeries
- Description: 메타데이터에 포함할 표적 객체 목록을 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:2394`, `Source/NXVideo/XUasMetadata.h:2399`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2773`, `Source/NXVideo/XUasMetadata.cpp:2779`

## SetTimeStamp
- Description: VMTI LS 타임스탬프.
- Declaration: `Source/NXVideo/XUasMetadata.h:2370`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2750`
