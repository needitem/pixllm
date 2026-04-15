---
title: Pixoneer.NXDL.NXVideo.XVideoFrameFilter Methods
aliases:
  - XVideoFrameFilter Methods
  - Pixoneer.NXDL.NXVideo.XVideoFrameFilter
  - XVideoFrameFilter
symbols:
  - XVideoFrameFilter
  - CleanUp
  - FilterProcess
  - SetVideoChannel
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
- Type: `XVideoFrameFilter`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XVideoFrameFilter.htm`
- Type declaration: `Source/NXVideo/XVideoChannel.h:94`
- Method count: `3`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XVideoFrameFilter
type_name: XVideoFrameFilter
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
## CleanUp
- Description: 필터 객체가 소멸할 때 필터 내부 데이터 정리와 같은 처리를 정의한다.
- Declaration: `Source/NXVideo/XVideoChannel.h:130`
- Implementation: `not found`

## FilterProcess
- Description: 필터 처리를 정의한다.
- Declaration: `Source/NXVideo/XVideoChannel.h:126`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:88`

## SetVideoChannel
- Description: 필터를 적용할 동영상 채널을 설정한다. dl 메소드는 채널에 필터를 추가할 때 자동으로 불린다.
- Declaration: `Source/NXVideo/XVideoChannel.h:119`
- Implementation: `Source/NXVideo/XVideoChannel.cpp:50`
