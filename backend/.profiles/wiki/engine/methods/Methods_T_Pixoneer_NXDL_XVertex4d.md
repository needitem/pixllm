---
title: Pixoneer.NXDL.XVertex4d Methods
aliases:
  - XVertex4d Methods
  - Pixoneer.NXDL.XVertex4d
  - XVertex4d
symbols:
  - XVertex4d
  - GetNormalize
  - IsEqual
  - norm
  - norm2
  - Normalize
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `XVertex4d`
- HTML source: `html/Methods_T_Pixoneer_NXDL_XVertex4d.htm`
- Type declaration: `Source/NXDL/NXDL.h:1423`
- Method count: `5`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.XVertex4d
type_name: XVertex4d
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
## GetNormalize
- Description: 이 객체의 노멀라이즈 결과값을 반환한다. 이 객체는 바뀌지 않는다.
- Declaration: `Source/NXDL/NXDL.h:1496`
- Implementation: `Source/NXDL/XVertex4d.cpp:94`

## IsEqual
- Description: 만약 입력 XVertex4d객체와 동일하다면 true를 반환하고 그렇지 않으면 false를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1487`
- Implementation: `Source/NXDL/XVertex4d.cpp:74`

## norm
- Description: 이 객체의 Euclidian Normalization을 수행한다.
- Declaration: `Source/NXDL/NXDL.h:1500`
- Implementation: `Source/NXDL/XVertex4d.cpp:100`

## norm2
- Description: 이 객체의 Euclidean Norm 제곱을 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1504`
- Implementation: `Source/NXDL/XVertex4d.cpp:105`

## Normalize
- Description: 이 객체의 값을 노멀라이즈한다. Normalization은 다음과 같다 : (x = x/sqrt(x*x + y*y + z*z + w*w), y = y/sqrt(x*x + y*y + z*z + w*w), z = z/sqrt(x*x + y*y + z*z + w*w), w = w/sqrt(x*x + y*y + z*z + w*w)).
- Declaration: `Source/NXDL/NXDL.h:1492`
- Implementation: `Source/NXDL/XVertex4d.cpp:85`
