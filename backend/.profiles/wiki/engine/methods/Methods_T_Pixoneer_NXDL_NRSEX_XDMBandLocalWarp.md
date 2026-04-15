---
title: Pixoneer.NXDL.NRSEX.XDMBandLocalWarp Methods
aliases:
  - XDMBandLocalWarp Methods
  - Pixoneer.NXDL.NRSEX.XDMBandLocalWarp
  - XDMBandLocalWarp
symbols:
  - XDMBandLocalWarp
  - GetInputParam
  - Preprocess
  - SetInputParam
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
- Type: `XDMBandLocalWarp`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRSEX_XDMBandLocalWarp.htm`
- Type declaration: `Source/NXDLrsEx/XDMBandLocalWarp.h:344`
- Method count: `3`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRSEX.XDMBandLocalWarp
type_name: XDMBandLocalWarp
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
## GetInputParam
- Description: 영상 정합을 위한 입력 파라미터를 얻는다.
- Declaration: `Source/NXDLrsEx/XDMBandLocalWarp.h:362`
- Implementation: `Source/NXDLrsEx/XDMBandLocalWarp.cpp:136`

## Preprocess
- Description: 정합점들로 Triangle을 생성하고 각 Triangle 에 대한 warping coeff (xr, yr) --> (xi, yi) 를 계산한다.
- Declaration: `Source/NXDLrsEx/XDMBandLocalWarp.h:369`
- Implementation: `Source/NXDLrsEx/XDMBandLocalWarp.cpp:155`

## SetInputParam
- Description: 영상 정합을 위한 입력 파라미터를 설정.
- Declaration: `Source/NXDLrsEx/XDMBandLocalWarp.h:358`
- Implementation: `Source/NXDLrsEx/XDMBandLocalWarp.cpp:91`
