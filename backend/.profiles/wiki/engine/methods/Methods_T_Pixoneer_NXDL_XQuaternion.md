---
title: Pixoneer.NXDL.XQuaternion Methods
aliases:
  - XQuaternion Methods
  - Pixoneer.NXDL.XQuaternion
  - XQuaternion
symbols:
  - XQuaternion
  - ConvAxis
  - Identity
  - IsIdentity
  - Normalize
  - Rotate
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `XQuaternion`
- HTML source: `html/Methods_T_Pixoneer_NXDL_XQuaternion.htm`
- Type declaration: `Source/NXDL/NXDL.h:1890`
- Method count: `5`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.XQuaternion
type_name: XQuaternion
namespace: Pixoneer.NXDL
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
## ConvAxis
- Description: XQuaternion 에 Axis 값을 곱한 rotation을 생성한다.
- Declaration: `Source/NXDL/NXDL.h:1950`
- Implementation: `Source/NXDL/XQuaternion.cpp:76`

## Identity
- Description: Identity rotation 으로 설정한다.
- Declaration: `Source/NXDL/NXDL.h:1925`
- Implementation: `Source/NXDL/XQuaternion.cpp:27`

## IsIdentity
- Description: Identity rotation 여부를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1929`
- Implementation: `Source/NXDL/XQuaternion.cpp:32`

## Normalize
- Description: XQuaternion 객체에 대한 Normalize를 수행한다.
- Declaration: `Source/NXDL/NXDL.h:1946`
- Implementation: `Source/NXDL/XQuaternion.cpp:69`

## Rotate
- Description: 축 Axis 를 angle 값만큼 회전한 rotation을 생성한다.
- Declaration: `Source/NXDL/NXDL.h:1936`, `Source/NXDL/NXDL.h:1941`
- Implementation: `Source/NXDL/XQuaternion.cpp:37`, `Source/NXDL/XQuaternion.cpp:48`, `Source/NXDL/XQuaternion.cpp:53`
