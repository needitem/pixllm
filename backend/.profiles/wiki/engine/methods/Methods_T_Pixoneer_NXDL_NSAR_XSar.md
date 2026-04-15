---
title: Pixoneer.NXDL.NSAR.XSar Methods
aliases:
  - XSar Methods
  - Pixoneer.NXDL.NSAR.XSar
  - XSar
symbols:
  - XSar
  - ApplyMatchedFilter
  - CalcACCC
  - CalcBackscatterCoefficient
  - CalcBackscatterCoefficientKompsat
  - CalcIncidenceAngles
  - CalcIncidenceAngleTargetOnWGS84
  - CalcLookAngles
  - GenerateIncidenceAngleMap
  - GetOrbitFromZeroDopplerTime
  - PreprocessInSAR
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nsar
---

# Overview
- Namespace: `Pixoneer.NXDL.NSAR`
- Type: `XSar`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NSAR_XSar.htm`
- Type declaration: `Source/NXDLsar/NXDLsar.h:120`
- Method count: `10`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NSAR.XSar
type_name: XSar
namespace: Pixoneer.NXDL.NSAR
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
## ApplyMatchedFilter
- Description: FFT 된 영상 신호에 MatchedFilter를 적용한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:169`
- Implementation: `Source/NXDLsar/NXDLsar.cpp:110`

## CalcACCC
- Description: ACCC(Average Cross Correlation Coefficient) 알고리즘 기반으로 신호 기반의 도플러 중심주파수를 추정한다.
- Declaration: `not found`
- Implementation: `not found`

## CalcBackscatterCoefficient
- Description: SAR 영상(K5)의 SLC data와 센서 정보를 이용해서 backscatter coefficient(sigma0, gamma0, beta0)를 float 크기로 계산한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:206`, `Source/NXDLsar/NXDLsar.h:227`, `Source/NXDLsar/NXDLsar.h:263`
- Implementation: `Source/NXDLsar/NXDLsar.cpp:165`, `Source/NXDLsar/NXDLsar.cpp:197`, `Source/NXDLsar/NXDLsar.cpp:344`

## CalcBackscatterCoefficientKompsat
- Description: SAR 영상 파일로 부터 SLC data와 센서 정보를 읽어 backscatter coefficient(sigma0, gamma0, beta0)를 float 크기로 계산한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:243`
- Implementation: `Source/NXDLsar/NXDLsar.cpp:229`

## CalcIncidenceAngles
- Description: SAR 센서 모델로부터 영상의 Azimuth 방향의 Index에 해당하는 Range 방향의 Incidence Angle을 계산한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:178`
- Implementation: `Source/NXDLsar/NXDLsar.cpp:127`

## CalcIncidenceAngleTargetOnWGS84
- Description: WGS84 타원체 환경에서 입력 궤도의 촬영 중심시점에서의 위성의 포인팅 위치 및 위성과 포인팅 위치의 incidence angle을 계산한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:137`
- Implementation: `Source/NXDLsar/NXDLsar.cpp:21`

## CalcLookAngles
- Description: SAR 센서 모델로부터 영상의 Azimuth 방향의 Index에 해당하는 Range 방향의 Look Angle을 계산한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:187`
- Implementation: `Source/NXDLsar/NXDLsar.cpp:146`

## GenerateIncidenceAngleMap
- Description: WGS84 타원체 환경에서 SAR 영상 촬영영역에 대하여 incidence angle의 맵을 사용자 지정 크기(nXSize, nYSize)로 생성한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:148`
- Implementation: `Source/NXDLsar/NXDLsar.cpp:61`

## GetOrbitFromZeroDopplerTime
- Description: 입력 궤도에서 촬영 중심 시점에 scene의 중심 위치를 지나는 위치, 속도를 반환한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:161`
- Implementation: `Source/NXDLsar/NXDLsar.cpp:74`

## PreprocessInSAR
- Description: InSAR를 형성하는 영상 쌍(A,B)을 입력받아 전처리를 수행한다.
- Declaration: `Source/NXDLsar/NXDLsar.h:280`
- Implementation: `Source/NXDLsar/NXDLsar.cpp:383`
