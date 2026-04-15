---
title: Pixoneer.NXDL.NIO.XDtedElevManager Methods
aliases:
  - XDtedElevManager Methods
  - Pixoneer.NXDL.NIO.XDtedElevManager
  - XDtedElevManager
symbols:
  - XDtedElevManager
  - GenerateXDMBandTileMerge
  - GetHeightAboveMSL
  - Open
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nio
---

# Overview
- Namespace: `Pixoneer.NXDL.NIO`
- Type: `XDtedElevManager`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NIO_XDtedElevManager.htm`
- Type declaration: `Source/NXDLio/NXDLio.h:949`
- Method count: `3`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NIO.XDtedElevManager
type_name: XDtedElevManager
namespace: Pixoneer.NXDL.NIO
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
## GenerateXDMBandTileMerge
- Description: DTED의 일부 영역에 대한 고도값을 얻기 위해 XDMBandTileMerge 객체를 생성한다.
- Declaration: `Source/NXDLio/NXDLio.h:976`
- Implementation: `Source/NXDLio/XDtedElevManager.cpp:54`

## GetHeightAboveMSL
- Description: 입력 좌표점에 대한 Mean SeaLevel상의 고도값을 얻는다. 입력 좌표 주변값을 이용하여 Bilinear interpolation을 한다.
- Declaration: `Source/NXDLio/NXDLio.h:968`
- Implementation: `Source/NXDLio/XDtedElevManager.cpp:49`

## Open
- Description: 로컬 디스크의 DTED가 존재하는 Folder를 입력하여 DTED값을 추출가능하도록 준비한다.
- Declaration: `Source/NXDLio/NXDLio.h:963`
- Implementation: `Source/NXDLio/XDtedElevManager.cpp:42`
