---
title: Pixoneer.NXDL.NCC.XCoordinateTransformation Methods
aliases:
  - XCoordinateTransformation Methods
  - Pixoneer.NXDL.NCC.XCoordinateTransformation
  - XCoordinateTransformation
symbols:
  - XCoordinateTransformation
  - CreateCoordinateTransform
  - TransformPt
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - ncc
---

# Overview
- Namespace: `Pixoneer.NXDL.NCC`
- Type: `XCoordinateTransformation`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NCC_XCoordinateTransformation.htm`
- Type declaration: `Source/NXDLcc/NXDLcc.h:274`
- Method count: `2`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NCC.XCoordinateTransformation
type_name: XCoordinateTransformation
namespace: Pixoneer.NXDL.NCC
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
## CreateCoordinateTransform
- Description: 입력되는 Input XSpatialReference 객체로부터 Output XSpatialReference 객체로의 변환을 위해 초기화한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:291`
- Implementation: `Source/NXDLcc/XCoordinateTransform.cpp:42`

## TransformPt
- Description: 설정된 좌표 시스템 간의 입력 좌표점으로부터 출력 좌표점으로 변환을 수행한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:301`, `Source/NXDLcc/NXDLcc.h:309`
- Implementation: `Source/NXDLcc/XCoordinateTransform.cpp:61`, `Source/NXDLcc/XCoordinateTransform.cpp:72`
