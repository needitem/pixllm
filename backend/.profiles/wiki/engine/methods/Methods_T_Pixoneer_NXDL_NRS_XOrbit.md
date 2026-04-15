---
title: Pixoneer.NXDL.NRS.XOrbit Methods
aliases:
  - XOrbit Methods
  - Pixoneer.NXDL.NRS.XOrbit
  - XOrbit
symbols:
  - XOrbit
  - GetAttitude
  - GetRPY
  - GetRPYDot
  - GetState
  - GetXYZ
  - GetXYZDDot
  - GetXYZDot
  - SetKLOKHI
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
- Type: `XOrbit`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XOrbit.htm`
- Type declaration: `Source/NXDLrs/XRSFile.h:756`
- Method count: `8`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XOrbit
type_name: XOrbit
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
## GetAttitude
- Description: time에 대응하는 자세와 변화 값을 계산하여 얻어온다.
- Declaration: `Source/NXDLrs/XRSFile.h:823`
- Implementation: `Source/NXDLrs/XOrbit.cpp:1090`

## GetRPY
- Description: Roll, Pitch, Yaw에 대한 Spline Interpolation을 통하여 자세 값을 계산하여 얻어온다.
- Declaration: `Source/NXDLrs/XRSFile.h:811`
- Implementation: `Source/NXDLrs/XOrbit.cpp:1052`

## GetRPYDot
- Description: Roll, Pitch, Yaw에 대한 Spline Interpolation을 통하여 자세의 변화 값을 계산하여 얻어온다.
- Declaration: `Source/NXDLrs/XRSFile.h:816`
- Implementation: `Source/NXDLrs/XOrbit.cpp:1071`

## GetState
- Description: time에 대응하는 위치, 속도, 가속도 값을 계산하여 얻어온다.
- Declaration: `Source/NXDLrs/XRSFile.h:792`, `Source/NXDLrs/XRSFile.h:801`
- Implementation: `Source/NXDLrs/XOrbit.cpp:725`, `Source/NXDLrs/XOrbit.cpp:730`

## GetXYZ
- Description: Coefficient X, Y, Z를 사용하여 위치 값을 계산하여 얻어온다.
- Declaration: `Source/NXDLrs/XRSFile.h:774`
- Implementation: `Source/NXDLrs/XOrbit.cpp:668`

## GetXYZDDot
- Description: Coefficient X, Y, Z 값을 사용하여 가속도 값을 계산하여 얻어온다.
- Declaration: `Source/NXDLrs/XRSFile.h:784`
- Implementation: `Source/NXDLrs/XOrbit.cpp:706`

## GetXYZDot
- Description: Coefficient X, Y, Z 값을 사용하여 속도 값을 계산하여 얻어온다.
- Declaration: `Source/NXDLrs/XRSFile.h:779`
- Implementation: `Source/NXDLrs/XOrbit.cpp:687`

## SetKLOKHI
- Description: 시간 값 t에 해당하는 Time 값의 인덱스 범위를 설정한다.
- Declaration: `Source/NXDLrs/XRSFile.h:806`
- Implementation: `Source/NXDLrs/XOrbit.cpp:758`
