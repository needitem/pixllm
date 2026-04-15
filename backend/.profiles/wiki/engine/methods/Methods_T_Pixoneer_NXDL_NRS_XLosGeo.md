---
title: Pixoneer.NXDL.NRS.XLosGeo Methods
aliases:
  - XLosGeo Methods
  - Pixoneer.NXDL.NRS.XLosGeo
  - XLosGeo
symbols:
  - XLosGeo
  - CalcVisible
  - IsVisible
  - SetDemBand
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
- Type: `XLosGeo`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XLosGeo.htm`
- Type declaration: `Source/NXDLrs/NXDLrs.h:1944`
- Method count: `3`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XLosGeo
type_name: XLosGeo
namespace: Pixoneer.NXDL.NRS
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
## CalcVisible
- Description: 설정된 DEM 밴드 상에서 기준점으로부터 배열 형태로 입력한 대상점들이 각각 보이는지 여부를 계산한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1982`
- Implementation: `Source/NXDLrs/XLosGeo.cpp:54`

## IsVisible
- Description: 설정된 DEM 밴드 상에서 입력한 두 점 간의 시점에서 상호 보이는지를 채크한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1966`, `Source/NXDLrs/NXDLrs.h:1975`
- Implementation: `Source/NXDLrs/XLosGeo.cpp:46`, `Source/NXDLrs/XLosGeo.cpp:86`

## SetDemBand
- Description: DEM 밴드를 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1959`
- Implementation: `Source/NXDLrs/XLosGeo.cpp:37`
