---
title: Pixoneer.NXDL.NRS.XDMBandNoiseInterpol Methods
aliases:
  - XDMBandNoiseInterpol Methods
  - Pixoneer.NXDL.NRS.XDMBandNoiseInterpol
  - XDMBandNoiseInterpol
symbols:
  - XDMBandNoiseInterpol
  - BuildAuxDataStructure
  - GetInputParam
  - ReadVerts
  - SetInputParam
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
- Type: `XDMBandNoiseInterpol`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XDMBandNoiseInterpol.htm`
- Type declaration: `Source/NXDLrs/XDMBandNoiseInterpol.h:155`
- Method count: `4`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XDMBandNoiseInterpol
type_name: XDMBandNoiseInterpol
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
## BuildAuxDataStructure
- Description: ReadVerts 함수를 통해 생성된 (x,y,z) 구조체를 이용해서 Interpolation 방법에 따른 잡음제거 구조체를 생성한다.
- Declaration: `Source/NXDLrs/XDMBandNoiseInterpol.h:192`
- Implementation: `Source/NXDLrs/XDMBandNoiseInterpol.cpp:108`

## GetInputParam
- Description: Noise Interpolation 영상처리를 위해 입력된 파라미터를 얻는다.
- Declaration: `Source/NXDLrs/XDMBandNoiseInterpol.h:178`
- Implementation: `Source/NXDLrs/XDMBandNoiseInterpol.cpp:94`

## ReadVerts
- Description: 입력 데이터에서 읽어 잡음으로 설정한 값인 경우 잡음 제거를 위해 (x,y,z(DN)) 형태의 구조체를 생성한다.
- Declaration: `Source/NXDLrs/XDMBandNoiseInterpol.h:185`
- Implementation: `Source/NXDLrs/XDMBandNoiseInterpol.cpp:99`

## SetInputParam
- Description: Noise Interpolation 영상처리를 위한 입력 파라미터를 설정한다.
- Declaration: `Source/NXDLrs/XDMBandNoiseInterpol.h:172`
- Implementation: `Source/NXDLrs/XDMBandNoiseInterpol.cpp:73`
