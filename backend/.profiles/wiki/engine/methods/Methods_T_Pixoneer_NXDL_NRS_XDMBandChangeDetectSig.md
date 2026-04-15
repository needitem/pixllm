---
title: Pixoneer.NXDL.NRS.XDMBandChangeDetectSig Methods
aliases:
  - XDMBandChangeDetectSig Methods
  - Pixoneer.NXDL.NRS.XDMBandChangeDetectSig
  - XDMBandChangeDetectSig
symbols:
  - XDMBandChangeDetectSig
  - CalcChangeStatistics
  - GetChangeStatistics
  - GetInputParam
  - SetInputParam
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nrs
---

# Overview
- Namespace: `Pixoneer.NXDL.NRS`
- Type: `XDMBandChangeDetectSig`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XDMBandChangeDetectSig.htm`
- Type declaration: `Source/NXDLrs/XDMBandChangeDetectSig.h:151`
- Method count: `4`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XDMBandChangeDetectSig
type_name: XDMBandChangeDetectSig
namespace: Pixoneer.NXDL.NRS
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
## CalcChangeStatistics
- Description: 특정영역에 대한 통계값을 설정하기 위해 변화 전과 변화 후의 ID를 대상으로 계산을 수행한다.
- Declaration: `Source/NXDLrs/XDMBandChangeDetectSig.h:178`
- Implementation: `Source/NXDLrs/XDMBandChangeDetectSig.cpp:92`

## GetChangeStatistics
- Description: 통계치를 계산한 후(CalcChangeStatistics 함수를 이용) 변경 전과 변경 후의 화소의 변경 자료를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandChangeDetectSig.h:184`
- Implementation: `Source/NXDLrs/XDMBandChangeDetectSig.cpp:105`

## GetInputParam
- Description: 객체에 설정된 입력 변수를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandChangeDetectSig.h:169`
- Implementation: `Source/NXDLrs/XDMBandChangeDetectSig.cpp:87`

## SetInputParam
- Description: 2장의 Signature 영상(XGIS Band)에 대한 변화탐지를 수행하기 위한 파라미터를 정의한 XBandParamChangeDetectSig객체를 설정한다.
- Declaration: `Source/NXDLrs/XDMBandChangeDetectSig.h:165`
- Implementation: `Source/NXDLrs/XDMBandChangeDetectSig.cpp:57`
