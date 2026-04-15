---
title: Pixoneer.NXDL.NXVideo.NXVideoTranscodeLayer Methods
aliases:
  - NXVideoTranscodeLayer Methods
  - Pixoneer.NXDL.NXVideo.NXVideoTranscodeLayer
  - NXVideoTranscodeLayer
symbols:
  - NXVideoTranscodeLayer
  - CropFrame
  - PauseTranscoding
  - ResumeTranscoding
  - SetEncoder
  - StartTranscoding
  - StopTranscoding
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
- Type: `NXVideoTranscodeLayer`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_NXVideoTranscodeLayer.htm`
- Type declaration: `Source/NXVideo/NXVideoLayerFunction.h:36`
- Method count: `6`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.NXVideoTranscodeLayer
type_name: NXVideoTranscodeLayer
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
## CropFrame
- Description: 입력 동영상에서 내보낼 화면 영역을 설정한다. 영역 설정을 하지 않으면 입력 영상 전체를 PRESERVE_RATIO_FULL 모드로 내보낸다.
- Declaration: `Source/NXVideo/NXVideoLayerFunction.h:61`
- Implementation: `Source/NXVideo/NXVideoLayerFunction.cpp:167`

## PauseTranscoding
- Description: 동영상 출력을 잠시 멈춘다.
- Declaration: `Source/NXVideo/NXVideoLayerFunction.h:66`
- Implementation: `Source/NXVideo/NXVideoLayerFunction.cpp:183`

## ResumeTranscoding
- Description: 동영상 출력을 재개한다.
- Declaration: `Source/NXVideo/NXVideoLayerFunction.h:68`
- Implementation: `Source/NXVideo/NXVideoLayerFunction.cpp:188`

## SetEncoder
- Description: 동영상 인코더를 설정한다.
- Declaration: `Source/NXVideo/NXVideoLayerFunction.h:52`
- Implementation: `Source/NXVideo/NXVideoLayerFunction.cpp:56`

## StartTranscoding
- Description: 동영상 출력을 시작한다.
- Declaration: `Source/NXVideo/NXVideoLayerFunction.h:64`
- Implementation: `Source/NXVideo/NXVideoLayerFunction.cpp:178`

## StopTranscoding
- Description: 동영상 출력을 종료한다. 인코더가 종료되므로 다시 동영상 출력을 할 수 없다.
- Declaration: `Source/NXVideo/NXVideoLayerFunction.h:70`
- Implementation: `Source/NXVideo/NXVideoLayerFunction.cpp:193`
