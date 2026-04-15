---
title: Pixoneer.NXDL.NSCENE.XScene Methods
aliases:
  - XScene Methods
  - Pixoneer.NXDL.NSCENE.XScene
  - XScene
symbols:
  - XScene
  - AddNode
  - Convert
  - Draw
  - GetDefaultDisplayOrder
  - GetNextID
  - GetNode
  - GetSequenceDisplayOrder
  - GetUserDisplayOrder
  - IsNodeExist
  - LoadScene
  - RemoveAllNode
  - RemoveNode
  - SaveScene
  - SetUserDisplayOrder
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nscene
---

# Overview
- Namespace: `Pixoneer.NXDL.NSCENE`
- Type: `XScene`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSCENE_XScene.htm`
- Type declaration: `Source/NXDLscene/NXDLscene.h:2465`
- Method count: `14`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSCENE.XScene
type_name: XScene
namespace: Pixoneer.NXDL.NSCENE
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
## AddNode
- Description: 객체를 컨테이너에 추가한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2503`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:127`

## Convert
- Description: Scene에서 공간 참조 대상에 맞게 변환하여 새로운 scene 객체를 반환한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2572`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:76`, `Source/NXDLscene/NXDLscene.cpp:87`

## Draw
- Description: 객체를 도시한다. 이것은 랜더 스레드로 실행된다 (Overrides XscObjDraw(NXDrawArgs, XscAttrSet))
- Declaration: `Source/NXDLscene/NXDLscene.h:2544`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:168`

## GetDefaultDisplayOrder
- Description: 디폴트 도시 순서의 객체 배열을 확인한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2521`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:218`

## GetNextID
- Description: 다음 새 객체의 새 ID를 확인한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2492`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:111`

## GetNode
- Description: 컨테이너로부터 객체를 확인한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2516`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:160`

## GetSequenceDisplayOrder
- Description: 입력 순서에 따른 도시 순서의 객체 배열을 확인한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2526`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:230`

## GetUserDisplayOrder
- Description: 사용자가 정한 도시 순서의 객체 배열을 확인한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2531`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:241`

## IsNodeExist
- Description: 사용 할 수 있는 ID인지 확인한다
- Declaration: `Source/NXDLscene/NXDLscene.h:2497`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:119`

## LoadScene
- Description: Scene 객체를 파일로부터 불러온다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2559`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:41`, `Source/NXDLscene/NXDLscene.cpp:45`

## RemoveAllNode
- Description: 컨테이너에서 모든 객체를 삭제한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2511`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:153`

## RemoveNode
- Description: 컨테이너에서 ID에 부합하는 객체를 삭제한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2508`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:145`

## SaveScene
- Description: Scene 객체를 파일로 저장한다.
- Declaration: `Source/NXDLscene/NXDLscene.h:2566`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:55`, `Source/NXDLscene/NXDLscene.cpp:73`

## SetUserDisplayOrder
- Description: 사용자가 정한 도시 순서를 배열에 설정한다 .
- Declaration: `Source/NXDLscene/NXDLscene.h:2536`
- Implementation: `Source/NXDLscene/NXDLscene.cpp:252`
