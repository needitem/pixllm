---
title: Pixoneer.NXDL.NSM.XOrbitInterpolator Methods
aliases:
  - XOrbitInterpolator Methods
  - Pixoneer.NXDL.NSM.XOrbitInterpolator
  - XOrbitInterpolator
symbols:
  - XOrbitInterpolator
  - AddStateVector
  - ClearStateVector
  - GetStateVector
  - HermiteInterpolate
  - IsValid
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
- Type: `XOrbitInterpolator`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSM_XOrbitInterpolator.htm`
- Type declaration: `Source/NXDLsm/NXDLsm.h:674`
- Method count: `5`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSM.XOrbitInterpolator
type_name: XOrbitInterpolator
namespace: Pixoneer.NXDL.NSM
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
## AddStateVector
- Description: 상태 벡터를 추가한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:690`
- Implementation: `Source/NXDLsm/XOrbitInterpolator.cpp:41`

## ClearStateVector
- Description: 저장된 모든 상태 벡터를 삭제한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:714`
- Implementation: `Source/NXDLsm/XOrbitInterpolator.cpp:97`

## GetStateVector
- Description: 특정 순서의 상태 벡터를 가져온다.
- Declaration: `Source/NXDLsm/NXDLsm.h:698`, `Source/NXDLsm/NXDLsm.h:707`
- Implementation: `Source/NXDLsm/XOrbitInterpolator.cpp:47`, `Source/NXDLsm/XOrbitInterpolator.cpp:68`

## HermiteInterpolate
- Description: 특정 시간에 대한 에르미트 보간법(Hermite interpolation)을 실행하고 그 때의 상태 벡터 값을 가져온다.
- Declaration: `Source/NXDLsm/NXDLsm.h:722`
- Implementation: `Source/NXDLsm/XOrbitInterpolator.cpp:103`

## IsValid
- Description: 특정 시간에 대해서 상태벡터의 보간이 가능한지 확인한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:711`
- Implementation: `Source/NXDLsm/XOrbitInterpolator.cpp:91`
