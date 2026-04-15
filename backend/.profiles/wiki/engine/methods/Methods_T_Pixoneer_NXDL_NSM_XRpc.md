---
title: Pixoneer.NXDL.NSM.XRpc Methods
aliases:
  - XRpc Methods
  - Pixoneer.NXDL.NSM.XRpc
  - XRpc
symbols:
  - XRpc
  - GetLosVector
  - GetRPCParam
  - GetSensorCenter
  - LoadFromRPC
  - SaveRPC
  - SetRPCParam
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
- Type: `XRpc`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSM_XRpc.htm`
- Type declaration: `Source/NXDLsm/NXDLsm.h:324`
- Method count: `6`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSM.XRpc
type_name: XRpc
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
## GetLosVector
- Description: 센서위치와 영상 좌표간의 방향벡터를 계산한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:378`
- Implementation: `Source/NXDLsm/XRpc.cpp:257`

## GetRPCParam
- Description: RPC 계수를 가져온다
- Declaration: `Source/NXDLsm/NXDLsm.h:373`
- Implementation: `Source/NXDLsm/XRpc.cpp:214`

## GetSensorCenter
- Description: 영상촬영시 센서의 진행방향의 중심 위치를 계산한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:383`
- Implementation: `Source/NXDLsm/XRpc.cpp:248`

## LoadFromRPC
- Description: RPC파일로부터 XRpc센서모델을 로딩한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:345`
- Implementation: `Source/NXDLsm/XRpc.cpp:59`

## SaveRPC
- Description: 생성된 RPC파일을 저장한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:350`
- Implementation: `Source/NXDLsm/XRpc.cpp:118`

## SetRPCParam
- Description: RPC 계수를 설정한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:362`
- Implementation: `Source/NXDLsm/XRpc.cpp:187`
