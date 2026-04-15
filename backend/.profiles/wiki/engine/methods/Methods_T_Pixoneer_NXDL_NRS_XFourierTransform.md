---
title: Pixoneer.NXDL.NRS.XFourierTransform Methods
aliases:
  - XFourierTransform Methods
  - Pixoneer.NXDL.NRS.XFourierTransform
  - XFourierTransform
symbols:
  - XFourierTransform
  - DFT1D
  - DFT2D
  - FFT1D
  - FFT1D_DNNP
  - FFT2D
  - FFT2D_DNNP
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
- Type: `XFourierTransform`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XFourierTransform.htm`
- Type declaration: `Source/NXDLrs/NXDLrs.h:2143`
- Method count: `6`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XFourierTransform
type_name: XFourierTransform
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
## DFT1D
- Description: 이산 푸리에 변환을 수행한다. 입출력 데이터 형식은 REAL32C, REAL64C만 유효하다. 입출력 데이터 XGrid 의 CSize = 1로 고정된다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2154`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:288`, `Source/NXDLrs/NXDLrs.cpp:310`, `Source/NXDLrs/NXDLrs.cpp:337`

## DFT2D
- Description: 이산 푸리에 변환을 수행하는 함수이다. 입출력 데이터 형식은 REAL32C, REAL64C만 유효하다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2163`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:367`, `Source/NXDLrs/NXDLrs.cpp:381`, `Source/NXDLrs/NXDLrs.cpp:407`

## FFT1D
- Description: 고속 푸리에 변환을 수행한다.(DPNN : DC-Positve-Nyquist-Negative Order). 입출력 데이터 형식은 REAL32C, REAL64C Type만 유효하다. 입출력 데이터 XGrid의 CSize = 1로 고정된다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2173`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:431`, `Source/NXDLrs/NXDLrs.cpp:446`, `Source/NXDLrs/NXDLrs.cpp:472`

## FFT1D_DNNP
- Description: 고속 푸리에 변환을 수행한다.(DNNP : DC-Negative-Nyquist-Positive Order). 입출력 데이터 형식은 REAL32C, REAL64C Type만 유효하다. 입출력 데이터 XGrid 의 CSize = 1로 고정된다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2194`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:563`, `Source/NXDLrs/NXDLrs.cpp:578`, `Source/NXDLrs/NXDLrs.cpp:606`

## FFT2D
- Description: 고속 푸리에 변환을 수행한다.(DPNN : DC-Positve-Nyquist-Negative Order). 입출력 데이터 형식은 REAL32C, REAL64C Type만 유효하다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2183`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:496`, `Source/NXDLrs/NXDLrs.cpp:510`, `Source/NXDLrs/NXDLrs.cpp:538`

## FFT2D_DNNP
- Description: 고속 푸리에 변환을 수행한다.(DNNP : DC-Negative-Nyquist-Positive Order). 입출력 데이터 형식은 REAL32C, REAL64C Type만 유효하다.
- Declaration: `Source/NXDLrs/NXDLrs.h:2204`
- Implementation: `Source/NXDLrs/NXDLrs.cpp:631`, `Source/NXDLrs/NXDLrs.cpp:645`, `Source/NXDLrs/NXDLrs.cpp:673`
