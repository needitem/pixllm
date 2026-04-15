---
title: Pixoneer.NXDL.NVC.XvcBase Methods
aliases:
  - XvcBase Methods
  - Pixoneer.NXDL.NVC.XvcBase
  - XvcBase
symbols:
  - XvcBase
  - AddHead
  - AddTail
  - CalcRange
  - FindIndex
  - GetBoundRect
  - GetHeadLayer
  - GetHeadLayerPos
  - GetLayer
  - GetLayerPos
  - GetNativePtr
  - GetNextLayerPos
  - GetNumLayers
  - GetPrevLayerPos
  - GetSR
  - GetTailLayerPos
  - HitTest
  - LoadFile
  - Normalize
  - RemoveAll
  - RemoveLayerPos
  - SaveFile
  - SetSR
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nvc
---

# Overview
- Namespace: `Pixoneer.NXDL.NVC`
- Type: `XvcBase`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NVC_XvcBase.htm`
- Type declaration: `Source/NXDLvc/NXDLvc.h:1410`
- Method count: `22`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NVC.XvcBase
type_name: XvcBase
namespace: Pixoneer.NXDL.NVC
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
## AddHead
- Description: 머리 위치에 레이어를 추가한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1472`
- Implementation: `Source/NXDLvc/XvcBase.cpp:63`

## AddTail
- Description: 꼬리 위치에 레이어를 추가한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1477`
- Implementation: `Source/NXDLvc/XvcBase.cpp:74`

## CalcRange
- Description: 경계 영역을 계산한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1525`
- Implementation: `Source/NXDLvc/XvcBase.cpp:238`

## FindIndex
- Description: 0부터 시작하는 순서로 지정된 객체의 위치를 가져온다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1482`
- Implementation: `Source/NXDLvc/XvcBase.cpp:85`

## GetBoundRect
- Description: 경계 영역의 최소/최댓값을 가져온다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1492`
- Implementation: `Source/NXDLvc/XvcBase.cpp:152`

## GetHeadLayer
- Description: 머리 위치에 있는 레이어를 가져온다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1467`
- Implementation: `Source/NXDLvc/XvcBase.cpp:147`

## GetHeadLayerPos
- Description: 머리 위치에 있는 레이어 위치값를 가져온다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1439`
- Implementation: `Source/NXDLvc/XvcBase.cpp:111`

## GetLayer
- Description: 특정 위치에 있는 레이어를 가져온다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1463`
- Implementation: `Source/NXDLvc/XvcBase.cpp:141`

## GetLayerPos
- Description: XvcLayer 객체의 위치값을 가져온다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1458`
- Implementation: `Source/NXDLvc/XvcBase.cpp:135`

## GetNativePtr
- Description: XvcBase의 원본 비관리 객체 포인터를 반환한다. C#에서 사용 불가.
- Declaration: `Source/NXDLvc/NXDLvc.h:1427`
- Implementation: `not found`

## GetNextLayerPos
- Description: 특정 위치 다음에 있는 레이어 위치값을 가져온다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1448`
- Implementation: `Source/NXDLvc/XvcBase.cpp:121`

## GetNumLayers
- Description: XvcBase에 포함되어 있는 레이어의 개수를 가져온다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1435`
- Implementation: `Source/NXDLvc/XvcBase.cpp:106`

## GetPrevLayerPos
- Description: 특정 위치 이전에 있는 레이어 특정 위치값을 가져온다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1453`
- Implementation: `Source/NXDLvc/XvcBase.cpp:128`

## GetSR
- Description: 지리 참조 좌표계를 가져온다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1500`
- Implementation: `Source/NXDLvc/XvcBase.cpp:172`

## GetTailLayerPos
- Description: 꼬리 위치에 있는 레이어 위치값을 가져온다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1443`
- Implementation: `Source/NXDLvc/XvcBase.cpp:116`

## HitTest
- Description: 특정 위치에 대해 객체가 선택되는지 테스트를 수행한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1508`, `Source/NXDLvc/NXDLvc.h:1515`
- Implementation: `Source/NXDLvc/XvcBase.cpp:182`, `Source/NXDLvc/XvcBase.cpp:205`

## LoadFile
- Description: 외부 파일로부터 XvcBase를 로딩한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1562`
- Implementation: `Source/NXDLvc/XvcBase.cpp:244`

## Normalize
- Description: 객체를 정규화한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1522`
- Implementation: `Source/NXDLvc/XvcBase.cpp:232`

## RemoveAll
- Description: 모든 레이어를 삭제한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1485`
- Implementation: `Source/NXDLvc/XvcBase.cpp:94`

## RemoveLayerPos
- Description: 특정 위치에 레이어를 삭제한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1431`
- Implementation: `Source/NXDLvc/XvcBase.cpp:100`

## SaveFile
- Description: 외부 파일로 XvcBase 객체를 저장한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1597`
- Implementation: `Source/NXDLvc/XvcBase.cpp:259`

## SetSR
- Description: 지리 참조 좌표계를 설정한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1496`
- Implementation: `Source/NXDLvc/XvcBase.cpp:164`
