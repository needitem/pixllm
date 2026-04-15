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
  - use_this_page_only_after_a_workflow_or_type_hint_narrows_scope
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page only as a verification layer after a workflow or explicit type hint identifies the target type.
- Cross-check declaration and implementation lines when overloads, properties, or call shapes matter.
- Do not synthesize end-to-end usage answers from this page alone.
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
