---
title: Pixoneer.NXDL.NXVideo.XFrameMetad Methods
aliases:
  - XFrameMetad Methods
  - Pixoneer.NXDL.NXVideo.XFrameMetad
  - XFrameMetad
symbols:
  - XFrameMetad
  - Decode
  - GetData
  - GetFrame
  - GetTargetByID
  - GetTargetIDs
  - MakeClone
  - SetData
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
- Type: `XFrameMetad`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XFrameMetad.htm`
- Type declaration: `Source/NXVideo/XFrameMetad.h:38`
- Method count: `7`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XFrameMetad
type_name: XFrameMetad
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
- Description: 기본 KLV 메타데이터 해석기로 디코딩한다. MISB ST 0601 일부 항목과 Predator UAV Basic Metadata에서 센서모델 파라미터 위주로 해석한다.
- Declaration: `Source/NXVideo/XFrameMetad.h:138`, `Source/NXVideo/XFrameMetad.h:143`
- Implementation: `Source/NXVideo/XFrameMetad.cpp:175`, `Source/NXVideo/XFrameMetad.cpp:190`

## GetData
- Description: 메타데이터 원본을 바이트 배열로 얻는다.
- Declaration: `Source/NXVideo/XFrameMetad.h:120`
- Implementation: `Source/NXVideo/XFrameMetad.cpp:213`

## GetFrame
- Description: 연결된 비관리 객체 포인터를 얻는다.
- Declaration: `Source/NXVideo/XFrameMetad.h:197`
- Implementation: `not found`

## GetTargetByID
- Description: 메타데이터에 보고된 표적을 식별자를 지정하여 얻는다.
- Declaration: `Source/NXVideo/XFrameMetad.h:208`
- Implementation: `Source/NXVideo/XFrameMetad.cpp:372`

## GetTargetIDs
- Description: 메타데이터에 보고된 표적 식별자 목록을 얻는다.
- Declaration: `Source/NXVideo/XFrameMetad.h:204`
- Implementation: `Source/NXVideo/XFrameMetad.cpp:351`

## MakeClone
- Description: 데이터 프레임 객체와 동일한 객체를 생성하여 반환한다.
- Declaration: `Source/NXVideo/XFrameMetad.h:194`
- Implementation: `Source/NXVideo/XFrameMetad.cpp:340`

## SetData
- Description: 메타데이터 원본을 교체한다. 이 메서드는 동영상 채널의 메타데이터 콜백(XVideoChannel.OnReceivedFrameMetad 맥락에서만 유효하다.
- Declaration: `Source/NXVideo/XFrameMetad.h:126`
- Implementation: `Source/NXVideo/XFrameMetad.cpp:225`
