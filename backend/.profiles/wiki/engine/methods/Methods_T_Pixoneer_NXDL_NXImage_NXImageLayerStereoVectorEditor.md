---
title: Pixoneer.NXDL.NXImage.NXImageLayerStereoVectorEditor Methods
aliases:
  - NXImageLayerStereoVectorEditor Methods
  - Pixoneer.NXDL.NXImage.NXImageLayerStereoVectorEditor
  - NXImageLayerStereoVectorEditor
symbols:
  - NXImageLayerStereoVectorEditor
  - CanPaste
  - CanRedo
  - CanUndo
  - Copy
  - CreateNewOBJ
  - Cut
  - Delete
  - EnableAttrSet
  - GetSelectedObjL
  - GetSelectedObjR
  - GetSelectedObjsL
  - GetSelectedObjsR
  - Group
  - HitTestL
  - HitTestR
  - Lock
  - Paste
  - Redo
  - SelectAll
  - SelectNone
  - SelectObject
  - Undo
  - UnGroup
  - UnLock
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
- Type: `NXImageLayerStereoVectorEditor`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXImage_NXImageLayerStereoVectorEditor.htm`
- Type declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:25`
- Method count: `24`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXImage.NXImageLayerStereoVectorEditor
type_name: NXImageLayerStereoVectorEditor
namespace: Pixoneer.NXDL.NXImage
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
## CanPaste
- Description: 편집작업에서 붙이기가 되는지 확인한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:67`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:368`

## CanRedo
- Description: 편집작업을 다시 할 수 있는지 확인한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:63`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:362`

## CanUndo
- Description: 편집작업을 취소할 수 있는지 확인한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:59`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:356`

## Copy
- Description: 선택된 객체를 복사한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:76`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:386`

## CreateNewOBJ
- Description: 기하 객체 형식에 부합하는 새로운 객체를 생성한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:108`, `Source/NXImage/NXImageLayerStereoVectorEditor.h:117`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:110`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:147`

## Cut
- Description: 선택된 객체를 잘라낸다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:79`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:392`

## Delete
- Description: 선택된 객체를 삭제한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:85`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:404`

## EnableAttrSet
- Description: 속성 세트를 적용할지 설정한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:55`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:104`

## GetSelectedObjL
- Description: 왼쪽에서 선택된 객체를 가져온다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:133`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:231`

## GetSelectedObjR
- Description: 오른쪽에서 선택된 객체를 가져온다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:137`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:240`

## GetSelectedObjsL
- Description: 왼쪽에서 선택된 객체 배열로 가져온다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:141`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:249`

## GetSelectedObjsR
- Description: 오른쪽에서 선택된 객체를 배열로 가져온다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:145`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:264`

## Group
- Description: 선택된 객체를 하나의 그룹으로 생성한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:89`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:410`

## HitTestL
- Description: 왼쪽에 대한 특정 위치에 해당 객체의 hit-testing을 수행한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:123`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:188`

## HitTestR
- Description: 오른쪽에 대한 특정 위치에 해당 객체의 hit-testing을 수행한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:129`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:210`

## Lock
- Description: 벡터 객체 편집 과정을 쓰레드 간에 접근하지 못하도록 제한한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:97`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:422`

## Paste
- Description: 복사된 객체를 붙인다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:82`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:398`

## Redo
- Description: 이전 작업을 다시 수행한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:73`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:380`

## SelectAll
- Description: 모든 객체를 선택한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:151`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:285`

## SelectNone
- Description: 객체의 선택을 해제한다. 어떤 객체가 선택되면, 선택된 것을 해제한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:148`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:279`

## SelectObject
- Description: 여러 개의 객체 중 하나의 객체만을 선택한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:157`, `Source/NXImage/NXImageLayerStereoVectorEditor.h:163`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:291`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:299`

## Undo
- Description: 이전 작업을 취소한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:70`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:374`

## UnGroup
- Description: 그룹 객체를 해제한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:93`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:416`

## UnLock
- Description: 벡터 객체 편집 제한을 해제한다.
- Declaration: `Source/NXImage/NXImageLayerStereoVectorEditor.h:101`
- Implementation: `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:428`
