---
title: Pixoneer.NXDL.NXVideo.XVMTILocalSetDecoder Methods
aliases:
  - XVMTILocalSetDecoder Methods
  - Pixoneer.NXDL.NXVideo.XVMTILocalSetDecoder
  - XVMTILocalSetDecoder
symbols:
  - XVMTILocalSetDecoder
  - Decode
  - Dispose
  - GetNativeDecoder
  - GetValue
  - SetFrameCenter
  - SetFrameSize
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
- Type: `XVMTILocalSetDecoder`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XVMTILocalSetDecoder.htm`
- Type declaration: `Source/NXVideo/XUasMetadata.h:2265`
- Method count: `6`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XVMTILocalSetDecoder
type_name: XVMTILocalSetDecoder
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
- Description: VMTI LS 메타데이터 패킷을 디코딩하고 태그 항목별 값 목록을 만든다.
- Declaration: `Source/NXVideo/XUasMetadata.h:2316`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2559`

## Dispose
- Description: 소멸자. 즉시 종료자를 부른다.
- Declaration: `not found`
- Implementation: `not found`

## GetNativeDecoder
- Description: XDL 내부 비관리 객체인 VMTI Local Set 메타데이터 디코더 포인터를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:2339`
- Implementation: `not found`

## GetValue
- Description: 메타데이터 태그를 지정하여 해당 항목의 인코딩 데이터를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:2335`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2530`

## SetFrameCenter
- Description: 표적 객체 위치의 기준이 되는 영상 프레임 중심점의 지리좌표를 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:2294`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2554`

## SetFrameSize
- Description: 표적 객체 화소 위치의 기준이 되는 대상 영상 프레임의 크기를 설정한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:2288`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:2549`
