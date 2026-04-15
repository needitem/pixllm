---
title: Pixoneer.NXDL.NXImage.NXImageLayer Methods
aliases:
  - NXImageLayer Methods
  - Pixoneer.NXDL.NXImage.NXImageLayer
  - NXImageLayer
symbols:
  - NXImageLayer
  - EnableShaderAlgorithm
  - GenShaderCodeAverage
  - GenShaderCodeBasso
  - GenShaderCodeCBS
  - GenShaderCodeEdge
  - GenShaderCodeHDR
  - GenShaderCodeMedian
  - GenShaderCodeNew
  - GetCartoonEffect
  - GetFilterSize
  - GetFilterType
  - GetNativePtr
  - GetShaderCBS
  - GetShaderGamma
  - SetCartoonEffect
  - SetFilterSize
  - SetFilterType
  - SetShaderAlgorithm
  - SetShaderCBS
  - SetShaderGamma
  - SetShaderHDR
  - SetShaderInvert
  - UpdateCursor
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nximage
---

# Overview
- Namespace: `Pixoneer.NXDL.NXImage`
- Type: `NXImageLayer`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXImage_NXImageLayer.htm`
- Type declaration: `Source/NXImage/NXImageLayer.h:23`
- Method count: `23`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXImage.NXImageLayer
type_name: NXImageLayer
namespace: Pixoneer.NXDL.NXImage
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
## EnableShaderAlgorithm
- Description: 쉐이더 알고리즘을 적용할지를 설정한다.
- Declaration: `Source/NXImage/NXImageLayer.h:101`
- Implementation: `Source/NXImage/NXImageLayer.cpp:33`

## GenShaderCodeAverage
- Description: Average 필터를 위한 기본 쉐이더 코드를 생성한다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXImage/NXImageLayer.h:202`
- Implementation: `Source/NXImage/NXImageLayer.cpp:222`

## GenShaderCodeBasso
- Description: Basso(Basso-rilievo(BAS-RELIEF) 필터를 위한 기본 쉐이더 코드를 생성한다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXImage/NXImageLayer.h:177`
- Implementation: `Source/NXImage/NXImageLayer.cpp:209`

## GenShaderCodeCBS
- Description: 화면 향상을 위한 대비, 채도, 명도값을 조절 쉐이더 코드를 문자열을 생성한다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXImage/NXImageLayer.h:119`
- Implementation: `Source/NXImage/NXImageLayer.cpp:170`

## GenShaderCodeEdge
- Description: Edge 필터를 위한 기본 쉐이더 코드를 생성한다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXImage/NXImageLayer.h:152`
- Implementation: `Source/NXImage/NXImageLayer.cpp:196`

## GenShaderCodeHDR
- Description: HDR 필터를 위한 기본 쉐이더 코드를 생성한다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXImage/NXImageLayer.h:127`
- Implementation: `Source/NXImage/NXImageLayer.cpp:183`

## GenShaderCodeMedian
- Description: Median 필터를 위한 기본 쉐이더 코드를 생성한다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXImage/NXImageLayer.h:227`
- Implementation: `Source/NXImage/NXImageLayer.cpp:235`

## GenShaderCodeNew
- Description: 기본 쉐이더 코드를 가져온다. 문자열로 반환된 코드를 받은 후, SetShaderAlgorithm 함수를 통해 설정해야 한다.
- Declaration: `Source/NXImage/NXImageLayer.h:111`
- Implementation: `Source/NXImage/NXImageLayer.cpp:159`

## GetCartoonEffect
- Description: Edge 필터에 적용되는 cartoonEffect 값을 가져온다.
- Declaration: `Source/NXImage/NXImageLayer.h:304`
- Implementation: `Source/NXImage/NXImageLayer.cpp:152`

## GetFilterSize
- Description: 필터 크기를 가져온다.
- Declaration: `Source/NXImage/NXImageLayer.h:239`
- Implementation: `Source/NXImage/NXImageLayer.cpp:60`

## GetFilterType
- Description: 필터 종류를 가져온다.
- Declaration: `Source/NXImage/NXImageLayer.h:266`
- Implementation: `Source/NXImage/NXImageLayer.cpp:91`

## GetNativePtr
- Description: NXImageLayer 원본 비관리 객체 포인터를 가져온다. c# 사용 불가.
- Declaration: `Source/NXImage/NXImageLayer.h:57`
- Implementation: `not found`

## GetShaderCBS
- Description: 대비, 명도, 채도값을 가져온다.
- Declaration: `Source/NXImage/NXImageLayer.h:279`
- Implementation: `Source/NXImage/NXImageLayer.cpp:107`

## GetShaderGamma
- Description: Gamma 값을 가져온다.
- Declaration: `Source/NXImage/NXImageLayer.h:288`
- Implementation: `Source/NXImage/NXImageLayer.cpp:124`

## SetCartoonEffect
- Description: Edge 필터의 CartoonEffect 값을 설정한다.
- Declaration: `Source/NXImage/NXImageLayer.h:300`
- Implementation: `Source/NXImage/NXImageLayer.cpp:145`

## SetFilterSize
- Description: 필터 크기를 설정한다.
- Declaration: `Source/NXImage/NXImageLayer.h:235`
- Implementation: `Source/NXImage/NXImageLayer.cpp:52`

## SetFilterType
- Description: 필터 종류를 설정한다.
- Declaration: `Source/NXImage/NXImageLayer.h:262`
- Implementation: `Source/NXImage/NXImageLayer.cpp:68`

## SetShaderAlgorithm
- Description: 사용자가 정의하는 쉐이더 알고리즘 문자열을 설정한다.
- Declaration: `Source/NXImage/NXImageLayer.h:106`
- Implementation: `Source/NXImage/NXImageLayer.cpp:41`

## SetShaderCBS
- Description: 대비, 명도, 채도값을 설정한다. EnableShaderAlgorithm 함수와 함께 사용한다.
- Declaration: `Source/NXImage/NXImageLayer.h:273`
- Implementation: `Source/NXImage/NXImageLayer.cpp:99`

## SetShaderGamma
- Description: Gamma 값을 설정한다. EnableShaderAlgorithm 함수와 함께 사용한다.
- Declaration: `Source/NXImage/NXImageLayer.h:284`
- Implementation: `Source/NXImage/NXImageLayer.cpp:117`

## SetShaderHDR
- Description: HDR Shader 적용 여부를 설정한다. EnableShaderAlgorithm 함수와 함께 사용한다.
- Declaration: `Source/NXImage/NXImageLayer.h:292`
- Implementation: `Source/NXImage/NXImageLayer.cpp:131`

## SetShaderInvert
- Description: Invert Shader 적용 여부를 설정한다. EnableShaderAlgorithm 함수와 함께 사용한다.
- Declaration: `Source/NXImage/NXImageLayer.h:296`
- Implementation: `Source/NXImage/NXImageLayer.cpp:138`

## UpdateCursor
- Description: 커서를 갱신한다.
- Declaration: `Source/NXImage/NXImageLayer.h:311`
- Implementation: `Source/NXImage/NXImageLayer.cpp:259`
