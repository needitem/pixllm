---
title: Pixoneer.NXDL.NSM.Xsm Methods
aliases:
  - Xsm Methods
  - Pixoneer.NXDL.NSM.Xsm
  - Xsm
symbols:
  - Xsm
  - GenerateRPCModel
  - GenerateRPCModelByCenter
  - GetSensorFootPrint
  - InverseRadialDistortion
  - IsRightLook
  - SpatialResection
  - UpdateRPC
  - UpdateRPCModel
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
- Type: `Xsm`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSM_Xsm.htm`
- Type declaration: `Source/NXDLsm/NXDLsm.h:735`
- Method count: `8`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSM.Xsm
type_name: Xsm
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
## GenerateRPCModel
- Description: GCP(XGCP객체)배열을 입력받아 RPC를 생성(XRpc객체)를 생성한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:794`, `Source/NXDLsm/NXDLsm.h:824`
- Implementation: `Source/NXDLsm/NXDLsm.cpp:25`, `Source/NXDLsm/NXDLsm.cpp:35`

## GenerateRPCModelByCenter
- Description: GCP(XGCP객체)배열을 입력받아 RPC를 생성(XRpc객체)를 생성한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:834`
- Implementation: `Source/NXDLsm/NXDLsm.cpp:55`

## GetSensorFootPrint
- Description: 센서위치로 부터 Foot Print의 네개의 코너점을 계산한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:906`
- Implementation: `Source/NXDLsm/NXDLsm.cpp:101`, `Source/NXDLsm/NXDLsm.cpp:104`

## InverseRadialDistortion
- Description: 영상의 방사왜곡에 대한 역변환 계수를 근사적으로 구한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:953`
- Implementation: `Source/NXDLsm/NXDLsm.cpp:196`, `Source/NXDLsm/NXDLsm.cpp:199`

## IsRightLook
- Description: 센서로부터 Scene 센터가 오른쪽에 있는지 판단한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:913`
- Implementation: `Source/NXDLsm/NXDLsm.cpp:114`, `Source/NXDLsm/NXDLsm.cpp:116`

## SpatialResection
- Description: 프레임 센서모델을 주어진 지상제어점을 이용하여 후방교회법으로 갱신한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:933`, `Source/NXDLsm/NXDLsm.h:941`
- Implementation: `Source/NXDLsm/NXDLsm.cpp:158`, `Source/NXDLsm/NXDLsm.cpp:163`, `Source/NXDLsm/NXDLsm.cpp:187`

## UpdateRPC
- Description: 기존 RPC를 입력 매개변수를 기준으로 갱신하여 새로운 RPC를 생성해서 반환한다. bOffsetOnly를 true로 설정하면 OffsetX, OffsetY 값만 사용하여 image offset을 조정한다. bOffsetPnly가 false인 경우 NumPixelX, NumPixelY 영상크기로 GCP를 생성하여 RPC를 갱신한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:926`
- Implementation: `Source/NXDLsm/NXDLsm.cpp:119`

## UpdateRPCModel
- Description: 기존의 RPC와 GCP점들을 이용하여 새로운 RPC모델을 생성한다.
- Declaration: `Source/NXDLsm/NXDLsm.h:866`, `Source/NXDLsm/NXDLsm.h:893`
- Implementation: `Source/NXDLsm/NXDLsm.cpp:75`, `Source/NXDLsm/NXDLsm.cpp:95`
