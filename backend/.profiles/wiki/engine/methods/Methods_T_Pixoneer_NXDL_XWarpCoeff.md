---
title: Pixoneer.NXDL.XWarpCoeff Methods
aliases:
  - XWarpCoeff Methods
  - Pixoneer.NXDL.XWarpCoeff
  - XWarpCoeff
symbols:
  - XWarpCoeff
  - CreateRotation
  - GetHomographyMatrix
  - GetWarpCoefficient
  - IsUnchanged
  - SetHomographyMatrix
  - SetWarpCoefficient
  - WarpPoint
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `XWarpCoeff`
- HTML source: `html/Methods_T_Pixoneer_NXDL_XWarpCoeff.htm`
- Type declaration: `Source/NXDL/NXDL.h:2031`
- Method count: `7`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.XWarpCoeff
type_name: XWarpCoeff
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
## CreateRotation
- Description: 회전각도와 센터 좌표를 입력 받아 영상변환계수를 산출한다. 이후 WarpPoint에 대한 좌표 변환은 입력된 센터 및 회전각을 적용한 좌표가 산출된다.
- Declaration: `Source/NXDL/NXDL.h:2076`
- Implementation: `Source/NXDL/XWarpCoeff.cpp:89`

## GetHomographyMatrix
- Description: Homography 행렬을 가져온다. 변환식이 eWarpMethod.Homography인 경우에만 유효하다.
- Declaration: `Source/NXDL/NXDL.h:2100`
- Implementation: `Source/NXDL/XWarpCoeff.cpp:202`

## GetWarpCoefficient
- Description: XWarpCoeff의 변환 계수를 가져온다.
- Declaration: `Source/NXDL/NXDL.h:2082`, `Source/NXDL/NXDL.h:2089`
- Implementation: `Source/NXDL/XWarpCoeff.cpp:97`, `Source/NXDL/XWarpCoeff.cpp:131`

## IsUnchanged
- Description: WarpPoint함수 수행시 입력 좌표가 출력 좌표와 동일한 경우 true를 반환하고, 아닌 경우 false를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:2054`
- Implementation: `Source/NXDL/XWarpCoeff.cpp:61`

## SetHomographyMatrix
- Description: 변환식 종류를 eWarpMethod.Homography로 설정하고 투영 변환 행렬을 설정한다.
- Declaration: `Source/NXDL/NXDL.h:2105`
- Implementation: `Source/NXDL/XWarpCoeff.cpp:211`

## SetWarpCoefficient
- Description: XWarpCoeff의 변환 계수를 설정한다.
- Declaration: `Source/NXDL/NXDL.h:2096`
- Implementation: `Source/NXDL/XWarpCoeff.cpp:167`

## WarpPoint
- Description: 입력되는 x, y좌표값을 영상 변환계수를 이용하여 좌표를 변환한다.
- Declaration: `Source/NXDL/NXDL.h:2061`, `Source/NXDL/NXDL.h:2068`
- Implementation: `Source/NXDL/XWarpCoeff.cpp:67`, `Source/NXDL/XWarpCoeff.cpp:78`
