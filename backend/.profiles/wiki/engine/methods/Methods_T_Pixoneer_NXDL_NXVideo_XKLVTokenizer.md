---
title: Pixoneer.NXDL.NXVideo.XKLVTokenizer Methods
aliases:
  - XKLVTokenizer Methods
  - Pixoneer.NXDL.NXVideo.XKLVTokenizer
  - XKLVTokenizer
symbols:
  - XKLVTokenizer
  - Dispose
  - GetNextOIDToken
  - GetNextSeriesToken
  - GetNextToken
  - GetNumberOfKLVTokens
  - GetNumberOfSeriesTokens
  - GetNumberOfTLVTokens
  - HasNextToken
  - SetPacket
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
- Type: `XKLVTokenizer`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XKLVTokenizer.htm`
- Type declaration: `Source/NXVideo/XUasMetadata.h:716`
- Method count: `9`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XKLVTokenizer
type_name: XKLVTokenizer
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
## Dispose
- Description: 소멸자. 소멸 즉시 종료자를 부른다.
- Declaration: `not found`
- Implementation: `not found`

## GetNextOIDToken
- Description: 다음 OID(Object Identifier)를 얻는다. TLV 항목의 태그 또는 다른 식별자일 수 있다.
- Declaration: `Source/NXVideo/XUasMetadata.h:804`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:655`

## GetNextSeriesToken
- Description: 값의 형태로 TLV와 달리 태그 항목 없이 길이-값의 집합으로 구성된 시리즈 항목을 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:792`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:631`

## GetNextToken
- Description: 데이터에서 다음 가용한 키-값 쌍을 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:760`, `Source/NXVideo/XUasMetadata.h:780`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:573`, `Source/NXVideo/XUasMetadata.cpp:606`

## GetNumberOfKLVTokens
- Description: 현재 분석 위치 이후 데이터에 포함된 전체 KLV 항목 개수를 얻는다. 순차적으로 놓인 항목만 세고 값 안에 내재된 항목은 세지 않는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:765`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:596`

## GetNumberOfSeriesTokens
- Description: 현재 분석 위치 이후 데이터에서 연속된 전체 시리즈 항목 개수를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:797`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:650`

## GetNumberOfTLVTokens
- Description: 현재 분석 위치 이후 데이터에 포함된 전체 TLV 항목 개수를 얻는다.
- Declaration: `Source/NXVideo/XUasMetadata.h:785`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:626`

## HasNextToken
- Description: 해석 중인 데이터가 남았는지 확인한다. 다음 항목이 있을 가능성만 보는 것으로 실제 가용 항목은 없을 수도 있다.
- Declaration: `Source/NXVideo/XUasMetadata.h:771`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:601`

## SetPacket
- Description: 해석할 데이터를 설정한다. 이후 항목 분석은 호출하는 메서드의 해석 방식을 따른다. 키 길이는 기본 16으로 한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:736`, `Source/NXVideo/XUasMetadata.h:744`, `Source/NXVideo/XUasMetadata.h:752`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:499`, `Source/NXVideo/XUasMetadata.cpp:517`, `Source/NXVideo/XUasMetadata.cpp:535`
