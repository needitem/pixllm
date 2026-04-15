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
  - use_this_page_only_after_a_workflow_or_type_hint_narrows_scope
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page only as a verification layer after a workflow or explicit type hint identifies the target type.
- Cross-check declaration and implementation lines when overloads, properties, or call shapes matter.
- Do not synthesize end-to-end usage answers from this page alone.
## CreateCoordinateTransform
- Description: 입력되는 Input XSpatialReference 객체로부터 Output XSpatialReference 객체로의 변환을 위해 초기화한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:291`
- Implementation: `Source/NXDLcc/XCoordinateTransform.cpp:42`

## TransformPt
- Description: 설정된 좌표 시스템 간의 입력 좌표점으로부터 출력 좌표점으로 변환을 수행한다.
- Declaration: `Source/NXDLcc/NXDLcc.h:301`, `Source/NXDLcc/NXDLcc.h:309`
- Implementation: `Source/NXDLcc/XCoordinateTransform.cpp:61`, `Source/NXDLcc/XCoordinateTransform.cpp:72`
