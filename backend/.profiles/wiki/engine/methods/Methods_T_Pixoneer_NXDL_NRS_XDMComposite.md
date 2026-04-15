---
title: Pixoneer.NXDL.NRS.XDMComposite Methods
aliases:
  - XDMComposite Methods
  - Pixoneer.NXDL.NRS.XDMComposite
  - XDMComposite
symbols:
  - XDMComposite
  - AddHistPt
  - AddXValue
  - GetBand
  - GetBoundRect
  - GetBrightness
  - GetCLT
  - GetColorBalance
  - GetContrast
  - GetCurSubsetStatistics
  - GetCutMax
  - GetCutMin
  - GetCutType
  - GetDIBits
  - GetGammaValue
  - GetHideFlag
  - GetHistPtsList
  - GetIntensity000
  - GetIntensity255
  - GetNativePtr
  - GetNumOfHistPts
  - GetNumOfXValues
  - GetSaturation
  - GetSTB
  - GetStretchCoverage
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
- Type: `XDMComposite`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XDMComposite.htm`
- Type declaration: `Source/NXDLrs/NXDLrs.h:1395`
- Method count: `48`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XDMComposite
type_name: XDMComposite
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
## AddHistPt
- Description: 입력 인덱스에 대하여 Piecewise Linear Stretching을 적용하기 위해 경계값 및 Intensity 값을 추가한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1640`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:627`

## AddXValue
- Description: 입력 인덱스에 해당하는 Piecewise Linear를 적용하기 위한 X 값을 추가한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1661`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:647`

## GetBand
- Description: 입력 인덱스에 해당하는 영상 밴드를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1433`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:238`

## GetBoundRect
- Description: 공간 상의 경계 영역을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1596`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:328`

## GetBrightness
- Description: 설정된 밝기값을 얻는다(-255~255). Brightness is an attributes of visual perception in which a source appears to be radiating or reflecting light. Adjusted pixel value = original pixel + brightness adjustment value.
- Declaration: `Source/NXDLrs/NXDLrs.h:1555`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:475`

## GetCLT
- Description: 색상표를 가져온다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1604`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:434`

## GetColorBalance
- Description: Color balance 값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1579`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:499`

## GetContrast
- Description: 설정된 대비(Contrast) 값(-127~127)을 얻는다. Contrast is the difference in luminance or color that makes an object distinguishable. Adjusted pixel value = 128 + (original pixel - 128) * contrast adjustment value.
- Declaration: `Source/NXDLrs/NXDLrs.h:1562`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:483`

## GetCurSubsetStatistics
- Description: 입력 인덱스에 로딩된 데이터를 기준으로 현재 통계 정보를 얻는다. 통계값이 유효하지 않은 경우에는 계산하여 반환한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1695`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:768`

## GetCutMax
- Description: 대비 조절을 위한 최댓값을 반환한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1470`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:390`

## GetCutMin
- Description: 대비 조절을 위한 최솟값을 반환한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1460`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:380`

## GetCutType
- Description: 대비 조절을 위한 영상 데이터 최소 최댓값 계산하는 방법을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1450`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:370`

## GetDIBits
- Description: 색합성에 특정 영역의 영상을 도시하고 그 영상의 DIB 데이터를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1706`, `Source/NXDLrs/NXDLrs.h:1718`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:516`, `Source/NXDLrs/XDMComposite.cpp:524`

## GetGammaValue
- Description: 영상의 밝기 조절을 위해 입력 인덱스에 대응하는 감마(Gamma)값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1503`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:193`

## GetHideFlag
- Description: 입력 인덱스에 대응하는 영상의 도시 여부를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1589`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:318`

## GetHistPtsList
- Description: 입력 인덱스에 해당하는 Piecewise Linear에 대한 정점들의 배열과 Intensity값 배열을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1654`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:700`

## GetIntensity000
- Description: 입력 인덱스에 해당하는 Intensity 최솟값(histogram stretching에 적용)을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1624`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:605`

## GetIntensity255
- Description: 입력 인덱스에 해당하는 Intensity 최댓값(histogram stretching에 적용)을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1634`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:619`

## GetNativePtr
- Description: XDMComposite의 원본 비관리 객체 포인터를 가져온다. c# 사용 불가.
- Declaration: `Source/NXDLrs/NXDLrs.h:1415`
- Implementation: `not found`

## GetNumOfHistPts
- Description: 입력 인덱스에 해당하는 Piecewise Linear를 위한 정점들의 갯수를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1648`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:639`

## GetNumOfXValues
- Description: 입력 인덱스에 해당하는 Piecewise Linear를 위한 X 값들의 갯수를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1669`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:659`

## GetSaturation
- Description: 설정된 채도(Saturation) 값(-100 ~ 100)을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1567`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:491`

## GetSTB
- Description: Stretch Table을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1614`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:685`

## GetStretchCoverage
- Description: 대비 조절 통계치를 계산하는 영역 형태를 가져온다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1482`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:400`

## GetStretchType
- Description: 입력 인덱스에 해당하는 히스토그램 신장(stretching) 방법을 얻는다
- Declaration: `Source/NXDLrs/NXDLrs.h:1492`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:408`

## GetSubsetStatistics
- Description: 입력 인덱스에 로딩된 데이터를 기준으로 통계 정보를 계산하여 가져온다
- Declaration: `Source/NXDLrs/NXDLrs.h:1684`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:745`

## GetTransparentValue
- Description: 입력 인덱스에 해당하는 밴드에 투명하게 처리하도록 설정한 화소값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1519`, `Source/NXDLrs/NXDLrs.h:1525`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:340`, `Source/NXDLrs/XDMComposite.cpp:350`

## GetXValuesList
- Description: 입력 인덱스에 해당하는 Piecewise Linear에 대한 X 값들의 배열을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1674`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:725`

## RemoveAllHistPts
- Description: 입력 인덱스에 해당하는 Piecewise Linear를 위한 정점(중간점)들을 모두 삭제한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1644`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:633`

## RemoveAllXValues
- Description: 입력 인덱스에 해당하는 Piecewise Linear를 위한 X 값들을 모두 삭제한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1665`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:653`

## SetBand
- Description: 영상 밴드를 해당 인덱스에 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1423`, `Source/NXDLrs/NXDLrs.h:1428`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:81`, `Source/NXDLrs/XDMComposite.cpp:93`

## SetBandGIS
- Description: XDMComposite를 Gray나 RGB로 만들기 위해 SetBand를 사용하지만, 분류(Classification) 영상처리 결과를 도시할 때는 SetBandGIS를 사용한다. SetBandGIS 함수는 영상 밴드를 설정하면서 SetCutType, SetCutMin/Max, SetCLT 등의 함수를 자동으로 호출하여 GIS 밴드 도시를 일괄처리한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1440`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:106`

## SetBrightness
- Description: 도시 영상의 밝기를 변경하기 위해 Brightness(-255~255) 값을 설정한다. Brightness is an attributes of visual perception in which a source appears to be radiating or reflecting light. Adjusted pixel value = original pixel + brightness adjustment value.
- Declaration: `Source/NXDLrs/NXDLrs.h:1533`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:451`

## SetCLT
- Description: 색상표를 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1600`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:416`

## SetColorBalance
- Description: Color balance 값를 설정한다. Color Balance는 칼라 값의 강도 조절을 의미한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1573`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:469`

## SetContrast
- Description: 도시 영상의 대비(contrast)를 변경하기 위해 Contrast(-127~127) 값을 설정한다. Contrast is the difference in luminance or color that makes an object distinguishable. Adjusted pixel value = 128 + (original pixel - 128) * contrast adjustment value.
- Declaration: `Source/NXDLrs/NXDLrs.h:1541`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:457`

## SetCutMax
- Description: 대비 조절을 최댓값을 설정한다. SetCutType이 eCompCutType.User일 때 입력값이 적용된다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1465`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:165`

## SetCutMin
- Description: 대비 조절을 최솟값을 설정한다. SetCutType이 eCompCutType.User일 때 입력값이 적용된다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1455`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:158`

## SetCutType
- Description: 대비 조절을 위한 영상 데이터 최소 최댓값 계산하는 방법을 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1445`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:151`

## SetGammaValue
- Description: 영상 밝기 조절을 하기 위해 감마(Gamma)값을 설정한다. 해당 값은 감마 보정에 사용된다. 히스토그램 신장 방법 중 eCompStretchType.Gamma으로 설정된 경우 적용된다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1498`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:186`

## SetHideFlag
- Description: 입력 인덱스에 대응하는 영상을 도시할지 여부를 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1584`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:311`

## SetIntensity000
- Description: 입력 인덱스에 해당하는 Intensity 최솟값(histogram stretching에 적용)을 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1619`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:598`

## SetIntensity255
- Description: 입력 인덱스에 해당하는 Intensity 최댓값(histogram stretching에 적용)을 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1629`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:613`

## SetSaturation
- Description: 도시 영상의 채도(Saturation)를 변경하기 위해 값(-100~100)을 설정한다. 0으로 설정하면 채도가 적용되지 않는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1547`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:463`

## SetSTB
- Description: Stretch Table을 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1609`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:667`

## SetStretchCoverage
- Description: 대비 조절 통계치를 계산하는 영역에 대한 형태(eCompStretchCoverage)을 설정한다. 통계치를 계산하는 데에 입력 인덱스에 해당하는 밴드의 전체 영역을 이용할지(밴드에 저장된 통계값), 도시된 화면 영역에 대한 데이터로 계산한 것을 이용할지 정하게 된다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1477`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:172`

## SetStretchType
- Description: 입력 인덱스에 해당하는 히스토그램 신장(stretching) 방법을 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1487`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:179`

## SetTransparentValue
- Description: 입력 인덱스에 대응하는 밴드에 투명하게 처리해야 할 화소값을 설정한다. 예를 들어 검은 색의 영역을 투명하게 처리하고 싶은 경우는 0을 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1508`, `Source/NXDLrs/NXDLrs.h:1514`
- Implementation: `Source/NXDLrs/XDMComposite.cpp:251`, `Source/NXDLrs/XDMComposite.cpp:258`
