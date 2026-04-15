---
title: Pixoneer.NXDL.NRSEX.XGenPMAG Methods
aliases:
  - XGenPMAG Methods
  - Pixoneer.NXDL.NRSEX.XGenPMAG
  - XGenPMAG
symbols:
  - XGenPMAG
  - AddBaseGCP
  - GenerateGCP
  - GetAt
  - GetBaseGCPAt
  - GetImageBand
  - GetNumBaseGCP
  - GetReferenceBand
  - GetSearchRange
  - GetSize
  - RemoveAll
  - RemoveAllBaseGCP
  - RemoveAllTriWarp
  - SetImageBand
  - SetReferenceBand
  - SetSearchRange
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nrsex
---

# Overview
- Namespace: `Pixoneer.NXDL.NRSEX`
- Type: `XGenPMAG`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRSEX_XGenPMAG.htm`
- Type declaration: `Source/NXDLrsEx/XGenPMAG.h:22`
- Method count: `15`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRSEX.XGenPMAG
type_name: XGenPMAG
namespace: Pixoneer.NXDL.NRSEX
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
## AddBaseGCP
- Description: Base GCP 를 입력한다. 최소 3점 이상을 입력해야 한다.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:74`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:93`

## GenerateGCP
- Description: Base GCP를 이용해서 입력 영상과 참조 영상간의 매칭점을 생성한다.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:94`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:122`

## GetAt
- Description: 해당 인덱스의 매칭점을 가져온다.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:106`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:141`

## GetBaseGCPAt
- Description: 해당 인덱스의 Base GCP 를 가져온다.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:82`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:99`

## GetImageBand
- Description: 설정된 입력 영상을 가져온다.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:42`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:49`

## GetNumBaseGCP
- Description: 입력된 Base GCP 개수를 가져온다.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:86`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:110`

## GetReferenceBand
- Description: 설정된 참조 영상을 가져온다.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:50`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:64`

## GetSearchRange
- Description: 매칭점을 찾을 영역을 가져온다(이미지 좌표).
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:64`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:75`

## GetSize
- Description: 매칭점 개수를 가져온다.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:110`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:153`

## RemoveAll
- Description: 모든 매칭점을 삭제한다.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:97`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:135`

## RemoveAllBaseGCP
- Description: 모든 Base GCP를 삭제한다.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:89`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:116`

## RemoveAllTriWarp
- Description: Base GCP 를 이용하여 만든 Triangle 의 Warping coeff 를 모두 삭제한다.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:67`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:87`

## SetImageBand
- Description: 입력 영상 설정.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:38`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:39`

## SetReferenceBand
- Description: 참조 영상 설정.
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:46`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:54`

## SetSearchRange
- Description: 매칭점을 찾을 영역 설정(이미지 좌표).
- Declaration: `Source/NXDLrsEx/XGenPMAG.h:57`
- Implementation: `Source/NXDLrsEx/XGenPMAG.cpp:69`
