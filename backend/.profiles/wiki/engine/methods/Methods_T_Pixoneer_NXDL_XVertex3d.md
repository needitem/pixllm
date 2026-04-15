---
title: Pixoneer.NXDL.XVertex3d Methods
aliases:
  - XVertex3d Methods
  - Pixoneer.NXDL.XVertex3d
  - XVertex3d
symbols:
  - XVertex3d
  - crossProduct
  - dotProduct
  - GetAngle
  - GetNormalize
  - IsEqual
  - norm
  - norm2
  - Normalize
  - ToXVertex2d
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `XVertex3d`
- HTML source: `html/Methods_T_Pixoneer_NXDL_XVertex3d.htm`
- Type declaration: `Source/NXDL/NXDL.h:1138`
- Method count: `9`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.XVertex3d
type_name: XVertex3d
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
## crossProduct
- Description: Cross-Product 연산 후 결과를 반환한다.
- Declaration: `not found`
- Implementation: `Source/NXDL/XVertex3d.cpp:98`, `Source/NXDL/XVertex3d.cpp:104`

## dotProduct
- Description: 객체 자신과 외부 입력 객체간의 Dot-Product를 수행한다.
- Declaration: `Source/NXDL/NXDL.h:1234`, `Source/NXDL/NXDL.h:1239`
- Implementation: `Source/NXDL/XVertex3d.cpp:88`, `Source/NXDL/XVertex3d.cpp:93`

## GetAngle
- Description: 첫번째 피연산자인 XVertex3d객체와 두번째 피연산자인 XVertex3d객체와 원점(0, 0, 0)이 이루는 각도를 계산하여 반환한다.
- Declaration: `not found`
- Implementation: `Source/NXDL/XVertex3d.cpp:134`

## GetNormalize
- Description: 객체의 값을 노멀라이즈하여 결과를 반환한다. 이 객체의 값은 변경되지 않는다.
- Declaration: `Source/NXDL/NXDL.h:1246`
- Implementation: `Source/NXDL/XVertex3d.cpp:118`

## IsEqual
- Description: 만약 입력 XVertex3d객체와 동일하다면 true를 반환하고 그렇지 않으면 false를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1228`
- Implementation: `Source/NXDL/XVertex3d.cpp:72`

## norm
- Description: 이 객체의 Euclidian Normalization을 수행한다.
- Declaration: `Source/NXDL/NXDL.h:1250`
- Implementation: `Source/NXDL/XVertex3d.cpp:124`

## norm2
- Description: 이 객체의 Euclidean Norm의 제곱을 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1254`
- Implementation: `Source/NXDL/XVertex3d.cpp:129`

## Normalize
- Description: 이 객체를 노멀라이즈한다. Normalization은 다음식에 정의된다.(x = x/sqrt(x*x + y*y + z*z), y = y/sqrt(x*x + y*y + z*z), z = z/sqrt(x*x + y*y + z*z)).
- Declaration: `Source/NXDL/NXDL.h:1242`
- Implementation: `Source/NXDL/XVertex3d.cpp:110`

## ToXVertex2d
- Description: Xvertex3d를 Xvertex2d로 변환한다.
- Declaration: `not found`
- Implementation: `Source/NXDL/XVertex3d.cpp:139`
