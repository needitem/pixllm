---
title: Pixoneer.NXDL.NRS.XSIGSet Methods
aliases:
  - XSIGSet Methods
  - Pixoneer.NXDL.NRS.XSIGSet
  - XSIGSet
symbols:
  - XSIGSet
  - AddSIG
  - CalcStatistics
  - GetSIGAt
  - GetSIGSize
  - LoadSIGSet
  - RemoveAll
  - RemoveSIGAt
  - SaveSIGSet
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
- Type: `XSIGSet`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XSIGSet.htm`
- Type declaration: `Source/NXDLrs/NXDLrs.h:468`
- Method count: `8`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XSIGSet
type_name: XSIGSet
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
## AddSIG
- Description: Signature Set를 형성하기 위해 XSIG를 추가한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:481`
- Implementation: `Source/NXDLrs/XSIGSet.cpp:39`

## CalcStatistics
- Description: 입력된 밴드의 리스트에 대한 Signature리스트 들에 대한 통계값을 계산한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:513`
- Implementation: `Source/NXDLrs/XSIGSet.cpp:67`

## GetSIGAt
- Description: XSIGSet를 생성하기 위해 추가된 XSIG 중 해당 Index에 대한 XSIG를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:486`
- Implementation: `Source/NXDLrs/XSIGSet.cpp:44`

## GetSIGSize
- Description: XSIGSet을 구성한 XSIG의 개수를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:490`
- Implementation: `Source/NXDLrs/XSIGSet.cpp:52`

## LoadSIGSet
- Description: 저장된 Signature를 로딩한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:502`
- Implementation: `Source/NXDLrs/XSIGSet.cpp:81`

## RemoveAll
- Description: 모든 XSIG를 삭제한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:497`
- Implementation: `Source/NXDLrs/XSIGSet.cpp:62`

## RemoveSIGAt
- Description: XSIGSet를 생성하기 위해 추가된 XSIG 중 해당 Index에 대한 XSIG를 지운다.
- Declaration: `Source/NXDLrs/NXDLrs.h:494`
- Implementation: `Source/NXDLrs/XSIGSet.cpp:57`

## SaveSIGSet
- Description: Signature를 저장한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:507`
- Implementation: `Source/NXDLrs/XSIGSet.cpp:237`
