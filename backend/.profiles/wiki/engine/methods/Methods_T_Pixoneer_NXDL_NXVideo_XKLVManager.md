---
title: Pixoneer.NXDL.NXVideo.XKLVManager Methods
aliases:
  - XKLVManager Methods
  - Pixoneer.NXDL.NXVideo.XKLVManager
  - XKLVManager
symbols:
  - XKLVManager
  - AddByteArray
  - AddInt32
  - AddInt64
  - AddUInt32
  - AddUInt64
  - Clear
  - GetKey
  - GetKLVCount
  - GetValue
  - MakeKLVGroup
  - ParseKLVData
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
- Type: `XKLVManager`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XKLVManager.htm`
- Type declaration: `Source/NXVideo/XKLVManager.h:15`
- Method count: `11`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XKLVManager
type_name: XKLVManager
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
## AddByteArray
- Description: 객체에 Key-Value쌍을 추가한다. Key값은 16바이트의 Universal Key를 의미한다.
- Declaration: `Source/NXVideo/XKLVManager.h:78`
- Implementation: `Source/NXVideo/XKLVManager.cpp:140`

## AddInt32
- Description: 객체에 Key-Value쌍을 추가한다. Key값은 16바이트의 Universal Key를 의미한다.
- Declaration: `Source/NXVideo/XKLVManager.h:58`
- Implementation: `Source/NXVideo/XKLVManager.cpp:104`

## AddInt64
- Description: 객체에 Key-Value쌍을 추가한다. Key값은 16바이트의 Universal Key를 의미한다.
- Declaration: `Source/NXVideo/XKLVManager.h:68`
- Implementation: `Source/NXVideo/XKLVManager.cpp:122`

## AddUInt32
- Description: 객체에 Key-Value쌍을 추가한다. Key값은 16바이트의 Universal Key를 의미한다.
- Declaration: `Source/NXVideo/XKLVManager.h:63`
- Implementation: `Source/NXVideo/XKLVManager.cpp:113`

## AddUInt64
- Description: 객체에 Key-Value쌍을 추가한다. Key값은 16바이트의 Universal Key를 의미한다.
- Declaration: `Source/NXVideo/XKLVManager.h:73`
- Implementation: `Source/NXVideo/XKLVManager.cpp:131`

## Clear
- Description: 객체 내부의 KLV 데이터들을 모두 삭제한다.
- Declaration: `Source/NXVideo/XKLVManager.h:31`
- Implementation: `Source/NXVideo/XKLVManager.cpp:39`

## GetKey
- Description: 입력된 Index에 해당하는 Key값을 얻는다. Key값은 16바이트의 Universal Key를 의미한다.
- Declaration: `Source/NXVideo/XKLVManager.h:44`
- Implementation: `Source/NXVideo/XKLVManager.cpp:58`

## GetKLVCount
- Description: KLV 쌍의 갯수를 반환한다.
- Declaration: `Source/NXVideo/XKLVManager.h:39`
- Implementation: `Source/NXVideo/XKLVManager.cpp:53`

## GetValue
- Description: 입력된 Index에 해당하는 Value값을 얻는다.
- Declaration: `Source/NXVideo/XKLVManager.h:49`
- Implementation: `Source/NXVideo/XKLVManager.cpp:72`

## MakeKLVGroup
- Description: 추가된 KLV쌍 배열의 값들을 1개의 Byte 배열로 합하는 과정을 수행한다.
- Declaration: `Source/NXVideo/XKLVManager.h:53`
- Implementation: `Source/NXVideo/XKLVManager.cpp:90`

## ParseKLVData
- Description: 외부 데이터 KLV Byte Array로부터 Parsing을 수행하여 Key-Value 쌍 구조를 생성하여 Key를 통해 Value를 얻을수 있도록 한다.
- Declaration: `Source/NXVideo/XKLVManager.h:35`
- Implementation: `Source/NXVideo/XKLVManager.cpp:44`
