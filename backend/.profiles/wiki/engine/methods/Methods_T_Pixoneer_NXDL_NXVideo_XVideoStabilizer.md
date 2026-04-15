---
title: Pixoneer.NXDL.NXVideo.XVideoStabilizer Methods
aliases:
  - XVideoStabilizer Methods
  - Pixoneer.NXDL.NXVideo.XVideoStabilizer
  - XVideoStabilizer
symbols:
  - XVideoStabilizer
  - Feed
  - GetFrameParams
  - Reset
  - ResetVideoChannel
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
- Type: `XVideoStabilizer`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XVideoStabilizer.htm`
- Type declaration: `Source/NXVideo/NXVideoExtension.h:258`
- Method count: `5`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XVideoStabilizer
type_name: XVideoStabilizer
namespace: Pixoneer.NXDL.NXVideo
method_section_prefix: "## "
verification_rules:
  - treat_declaration_lines_as_symbol_existence_evidence
  - treat_implementation_lines_as_source_anchor_evidence
  - use_this_page_only_after_a_workflow_or_type_hint_narrows_scope
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page only as a verification layer after a workflow or explicit type hint identifies the target type.
- Cross-check declaration and implementation lines when overloads, properties, or call shapes matter.
- Do not synthesize end-to-end usage answers from this page alone.
## Feed
- Description: 떨림 보정할 새 동영상 프레임을 공급한다.
- Declaration: `Source/NXVideo/NXVideoExtension.h:295`
- Implementation: `Source/NXVideo/NXVideoExtension.cpp:591`

## GetFrameParams
- Description: 주어진 시점의 프레임 안정화 파라미터를 얻는다.
- Declaration: `Source/NXVideo/NXVideoExtension.h:302`
- Implementation: `Source/NXVideo/NXVideoExtension.cpp:603`

## Reset
- Description: 안정화 영상을 초기화한다. 그룹 크기를 재설정한다.
- Declaration: `Source/NXVideo/NXVideoExtension.h:287`, `Source/NXVideo/NXVideoExtension.h:290`
- Implementation: `Source/NXVideo/NXVideoExtension.cpp:581`, `Source/NXVideo/NXVideoExtension.cpp:586`

## ResetVideoChannel
- Description: 처리기에 설정된 채널을 제거한다.
- Declaration: `Source/NXVideo/NXVideoExtension.h:284`
- Implementation: `Source/NXVideo/NXVideoExtension.cpp:566`

## SetVideoChannel
- Description: 동영상 채널을 설정한다.
- Declaration: `Source/NXVideo/NXVideoExtension.h:281`
- Implementation: `Source/NXVideo/NXVideoExtension.cpp:545`
