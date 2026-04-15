---
title: Pixoneer.NXDL.NSAR.XIrf Methods
aliases:
  - XIrf Methods
  - Pixoneer.NXDL.NSAR.XIrf
  - XIrf
symbols:
  - XIrf
  - AnalysisIRF
  - Dispose
  - GetPatchFFT
  - GetPatchForContour
  - GetPatchOrg
  - GetPatchOver
  - ReCalcIRW
  - ReCalcISLR
  - ReCalcPSLR
  - SetISLRParams
  - SetSarParams
  - SetShift
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nsar
---

# Overview
- Namespace: `Pixoneer.NXDL.NSAR`
- Type: `XIrf`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSAR_XIrf.htm`
- Type declaration: `Source/NXDLsar/NXDLsar.h:577`
- Method count: `12`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSAR.XIrf
type_name: XIrf
namespace: Pixoneer.NXDL.NSAR
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
## AnalysisIRF
- Description: IRF 분석을 수행한다. 입사각과 추출된 영상을 사용자의 입력으로 부터 받아 분석 수행. 입력된 영상은 64 x 64 영역에 맞추어 분석.
- Declaration: `Source/NXDLsar/NXDLsar.h:628`, `Source/NXDLsar/NXDLsar.h:639`, `Source/NXDLsar/NXDLsar.h:649`, `Source/NXDLsar/NXDLsar.h:663`, `Source/NXDLsar/NXDLsar.h:675`, `Source/NXDLsar/NXDLsar.h:686`
- Implementation: `Source/NXDLsar/XIRF.cpp:196`, `Source/NXDLsar/XIRF.cpp:201`, `Source/NXDLsar/XIRF.cpp:206`, `Source/NXDLsar/XIRF.cpp:211`, `Source/NXDLsar/XIRF.cpp:240`, `Source/NXDLsar/XIRF.cpp:272`

## Dispose
- Description: No description in HTML reference.
- Declaration: `not found`
- Implementation: `not found`

## GetPatchFFT
- Description: 분석에 사용한 추출 영상의 FFT 결과 영상을 가져온다.
- Declaration: `Source/NXDLsar/NXDLsar.h:754`
- Implementation: `Source/NXDLsar/XIRF.cpp:383`

## GetPatchForContour
- Description: 분석에 사용한 추출 영상의 Contour를 그리기 위한 영상을 가져온다.(크기를 DB로 나타낸 영상)
- Declaration: `Source/NXDLsar/NXDLsar.h:763`, `Source/NXDLsar/NXDLsar.h:769`
- Implementation: `Source/NXDLsar/XIRF.cpp:426`, `Source/NXDLsar/XIRF.cpp:433`

## GetPatchOrg
- Description: 분석에 사용한 추출 영상을 가져온다.
- Declaration: `Source/NXDLsar/NXDLsar.h:748`
- Implementation: `Source/NXDLsar/XIRF.cpp:363`

## GetPatchOver
- Description: 분석에 사용한 추출 영상의 오버샘플링 결과 영상을 가져온다.
- Declaration: `Source/NXDLsar/NXDLsar.h:759`
- Implementation: `Source/NXDLsar/XIRF.cpp:406`

## ReCalcIRW
- Description: 해상도의 재계산을 수행한다.(파라메터 변경시)
- Declaration: `Source/NXDLsar/NXDLsar.h:692`
- Implementation: `Source/NXDLsar/XIRF.cpp:297`

## ReCalcISLR
- Description: ISLR 재계산을 수행한다.(파라메터 변경시)
- Declaration: `Source/NXDLsar/NXDLsar.h:707`
- Implementation: `Source/NXDLsar/XIRF.cpp:342`

## ReCalcPSLR
- Description: PSLR 재계산을 수행한다.(파라메터 변경시)
- Declaration: `Source/NXDLsar/NXDLsar.h:700`
- Implementation: `Source/NXDLsar/XIRF.cpp:318`

## SetISLRParams
- Description: ISLR 계산을 위한 방식을 설정한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:614`
- Implementation: `Source/NXDLsar/XIRF.cpp:191`

## SetSarParams
- Description: IRF 수행을 위한 SAR 영상의 파라메터를 설정한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:603`
- Implementation: `Source/NXDLsar/XIRF.cpp:168`

## SetShift
- Description: IRF 수행을 Shift 값을 설정한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:609`
- Implementation: `Source/NXDLsar/XIRF.cpp:186`
