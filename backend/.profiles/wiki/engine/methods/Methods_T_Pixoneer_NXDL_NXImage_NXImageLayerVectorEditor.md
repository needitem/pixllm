---
title: Pixoneer.NXDL.NXImage.NXImageLayerVectorEditor Methods
aliases:
  - NXImageLayerVectorEditor Methods
  - Pixoneer.NXDL.NXImage.NXImageLayerVectorEditor
  - NXImageLayerVectorEditor
symbols:
  - NXImageLayerVectorEditor
  - CanPaste
  - CanRedo
  - CanUndo
  - ClearLayer
  - Copy
  - CreateNewOBJ
  - Cut
  - Delete
  - EnableAttrSet
  - EndEditing
  - GetEditBase
  - GetLayerDisplayOrder
  - GetSelectedObj
  - GetSelectedObjs
  - Group
  - HitTest
  - InsertNewOBJ
  - Lock
  - Modify
  - MoveToBack
  - MoveToFirst
  - MoveToFront
  - MoveToLast
  - Paste
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nximage
---

# Overview
- Namespace: `Pixoneer.NXDL.NXImage`
- Type: `NXImageLayerVectorEditor`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXImage_NXImageLayerVectorEditor.htm`
- Type declaration: `Source/NXImage/NXImageLayerVectorEditor.h:27`
- Method count: `34`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXImage.NXImageLayerVectorEditor
type_name: NXImageLayerVectorEditor
namespace: Pixoneer.NXDL.NXImage
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
## CanPaste
- Description: 편집작업에서 붙이기가 되는지 확인한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:79`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:363`

## CanRedo
- Description: 편집작업을 다시 할 수 있는지 확인한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:75`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:357`

## CanUndo
- Description: 편집작업을 취소할 수 있는지 확인한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:71`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:351`

## ClearLayer
- Description: 벡터 레이어에 도시된 객체를 모두 삭제한다. Undo/Redo command 도 모두 삭제된다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:411`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:97`

## Copy
- Description: 선택된 객체를 복사한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:88`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:381`

## CreateNewOBJ
- Description: 객체 형식과 정점 배열을 이용하여 새로운 객체를 생성한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:286`, `Source/NXImage/NXImageLayerVectorEditor.h:325`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:182`, `Source/NXImage/NXImageLayerVectorEditor.cpp:187`

## Cut
- Description: 선택된 객체를 잘라낸다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:91`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:387`

## Delete
- Description: 선택된 객체를 삭제한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:97`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:399`

## EnableAttrSet
- Description: 속성 세트를 적용할지 설정한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:67`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:67`

## EndEditing
- Description: 현재 객체 편집 과정을 종료한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:434`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:145`

## GetEditBase
- Description: 편집을 위한 베이스 객체을 가져온다.(XvcBase는 하나 이상의 레이어로 구성되며, 레이어(XvcLayer)는 여러 개의 객체로 포함한다.)
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:367`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:73`

## GetLayerDisplayOrder
- Description: 편집 베이스(EditBase)의 레이어(XvcLayer)들의 도시 순서 배열을 가져온다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:415`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:103`

## GetSelectedObj
- Description: 현재 선택된 객체를 가져온다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:335`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:233`

## GetSelectedObjs
- Description: 현재 선택된 객체 배열을 가져온다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:339`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:242`

## Group
- Description: 선택된 객체를 하나의 그룹으로 생성한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:101`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:405`

## HitTest
- Description: 특정 위치에 해당 객체의 hit-testing을 수행한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:331`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:212`

## InsertNewOBJ
- Description: 객체 형식과 정점 배열을 이용하여 새로운 객체를 추가한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:147`, `Source/NXImage/NXImageLayerVectorEditor.h:187`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:152`, `Source/NXImage/NXImageLayerVectorEditor.cpp:157`

## Lock
- Description: 벡터 객체 편집 과정을 쓰레드 간에 접근하지 못하도록 제한한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:427`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:133`

## Modify
- Description: 원본 객체와 수정 객체를 입력하여 편집 스택에 추가한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:111`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:417`

## MoveToBack
- Description: 선택된 객체를 한 단계 뒤로 도시한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:123`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:464`

## MoveToFirst
- Description: 선택된 객체를 맨 앞으로 도시한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:114`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:446`

## MoveToFront
- Description: 선택된 객체를 한 단계 앞으로 도시한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:117`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:452`

## MoveToLast
- Description: 선택된 객체를 맨 뒤로 도시한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:120`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:458`

## Paste
- Description: 복사된 객체를 붙인다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:94`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:393`

## Redo
- Description: 이전 작업을 다시 수행한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:85`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:375`

## SelectAll
- Description: 모든 객체를 선택한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:345`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:263`

## SelectNone
- Description: 객체 선택을 해제한다. 객체가 선택되면 이를 해제한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:342`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:257`

## SelectObject
- Description: 여러 개의 객체를 선택한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:351`, `Source/NXImage/NXImageLayerVectorEditor.h:356`, `Source/NXImage/NXImageLayerVectorEditor.h:362`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:269`, `Source/NXImage/NXImageLayerVectorEditor.cpp:278`, `Source/NXImage/NXImageLayerVectorEditor.cpp:296`

## SetEditBase
- Description: 이 레이어 밖에서 생성된 XvcBase 인스턴스를 설정한다. 외부 XvcBase를 설정하면 새로이 생성되는 객체는 외부 XvcBase에 추가된다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:401`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:82`

## SetEditLayer
- Description: 편집 레이어를 설정한다. 편집 베이스의 첫번째 레이어를 편집 레이어로 기본 설정하는데 이를 변경할 수 있다. 설정하는 편집 레이어는 편집 베이스(EditBase)의 레이어 중 하나이어야 한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:408`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:90`

## SetLayerDisplayOrder
- Description: 편집 베이스(EditBase)의 레이어(XvcLayer)의 ID를 배열에 차례로 저장하여 도시 순서를 설정한다. UsableLayerDisplayOrder가 true로 설정되어 있어야 하며, 맨 처음 항목의 XvcLayer가 먼저 도시된다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:423`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:116`

## Undo
- Description: 이전 작업을 취소한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:82`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:369`

## UnGroup
- Description: 그룹 객체를 해제한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:105`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:411`

## UnLock
- Description: 벡터 객체 편집 제한을 해제한다.
- Declaration: `Source/NXImage/NXImageLayerVectorEditor.h:431`
- Implementation: `Source/NXImage/NXImageLayerVectorEditor.cpp:139`
