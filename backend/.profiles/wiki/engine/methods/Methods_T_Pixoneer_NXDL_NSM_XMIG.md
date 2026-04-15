---
title: Pixoneer.NXDL.NSM.XMIG Methods
aliases:
  - XMIG Methods
  - Pixoneer.NXDL.NSM.XMIG
  - XMIG
symbols:
  - XMIG
  - ExtractPosition
  - GetConvergenceRate
  - GetImageOptPoints
  - GetParams
  - SetImagePoints
  - SetParams
  - SetSensorModels
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nsm
---

# Overview
- Namespace: `Pixoneer.NXDL.NSM`
- Type: `XMIG`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSM_XMIG.htm`
- Type declaration: `Source/NXDLsm/NXDLsm.h:418`
- Method count: `7`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSM.XMIG
type_name: XMIG
namespace: Pixoneer.NXDL.NSM
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
## ExtractPosition
- Description: 입력된 다중 센서정보와 입력된 이미지 좌표로부터 지리적인 위치를 결정한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:434`, `Source/NXDLsm/NXDLsm.h:440`, `Source/NXDLsm/NXDLsm.h:444`
- Implementation: `Source/NXDLsm/XMIG.cpp:38`, `Source/NXDLsm/XMIG.cpp:61`, `Source/NXDLsm/XMIG.cpp:83`

## GetConvergenceRate
- Description: 지리적인 위치를 결정한 수렴값을 가져온다.
- Declaration: `Source/NXDLsm/NXDLsm.h:466`
- Implementation: `Source/NXDLsm/XMIG.cpp:151`

## GetImageOptPoints
- Description: 지리적인 위치를 결정하기 위한 센서모델에 대응되는 이미지 좌표를 설정한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:453`
- Implementation: `Source/NXDLsm/XMIG.cpp:117`

## GetParams
- Description: 지리적인 위치를 결정하기 위한 수렴조건값을 가져온다.
- Declaration: `Source/NXDLsm/NXDLsm.h:462`
- Implementation: `Source/NXDLsm/XMIG.cpp:140`

## SetImagePoints
- Description: 지리적인 위치를 결정하기 위한 센서모델에 대응되는 이미지 좌표를 설정한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:450`
- Implementation: `Source/NXDLsm/XMIG.cpp:104`

## SetParams
- Description: 지리적인 위치를 결정하기 위한 수렴조건을 설정한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:458`
- Implementation: `Source/NXDLsm/XMIG.cpp:132`

## SetSensorModels
- Description: 지리적인 위치를 결정하기 위한 다중 센서정보를 설정한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:447`
- Implementation: `Source/NXDLsm/XMIG.cpp:92`
