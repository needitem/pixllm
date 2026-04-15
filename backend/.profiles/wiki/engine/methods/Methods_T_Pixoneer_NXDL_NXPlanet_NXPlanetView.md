---
title: Pixoneer.NXDL.NXPlanet.NXPlanetView Methods
aliases:
  - NXPlanetView Methods
  - Pixoneer.NXDL.NXPlanet.NXPlanetView
  - NXPlanetView
symbols:
  - NXPlanetView
  - AddRenderLayer
  - CalcSize
  - CalculateCADRGScale
  - CalculateScale
  - CaptureScreen
  - CaptureScreenByBlock
  - ChangeLayerOrder
  - ClearLayer
  - GeographicToScreen
  - GeographicToWorld
  - GetCameraState
  - GetDrawArgs
  - GetFreezeViewArea
  - GetHandle
  - GetIndexMapMode
  - GetLayer
  - GetLayerOrder
  - GetMapAlitutdeFromCADRGScale
  - GetMapAltitude
  - GetMouseControlMode
  - GetPTMOverlayLayer
  - GetWOS
  - IsUnderMouse
  - LookTarget
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nxplanet
---

# Overview
- Namespace: `Pixoneer.NXDL.NXPlanet`
- Type: `NXPlanetView`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXPlanet_NXPlanetView.htm`
- Type declaration: `Source/NXPlanet/NXPlanetView.h:220`
- Method count: `57`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXPlanet.NXPlanetView
type_name: NXPlanetView
namespace: Pixoneer.NXDL.NXPlanet
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
## AddRenderLayer
- Description: 뷰에 레이어를 추가한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:536`, `Source/NXPlanet/NXPlanetView.h:546`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:942`, `Source/NXPlanet/NXPlanetView.cpp:966`

## CalcSize
- Description: 뷰의 사이즈를 다시 계산하며, 엔진에 의해 자동 호출 된다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:457`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:537`

## CalculateCADRGScale
- Description: CADRG 축척에 따른 비율을 계산한다. CADRG NS PixelSize과의 비율을 이용하여 축척을 계산하여 반환한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1547`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2049`

## CalculateScale
- Description: 현재 뷰의 스케일을 계산한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1543`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2042`

## CaptureScreen
- Description: 현재 화면을 그대로 캡쳐한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:812`, `Source/NXPlanet/NXPlanetView.h:891`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:990`, `Source/NXPlanet/NXPlanetView.cpp:1001`, `Source/NXPlanet/NXPlanetView.cpp:1028`

## CaptureScreenByBlock
- Description: Planet View에 도시되어 있는 내용을 임시 PlanetView 를 이용하여 해상도 조절하여 저장한다. 임시 PlanetView 의 Width, Height 는 256 보다 큰 값으로 각각 설정한다. Planet2D 모드에서만 가능
- Declaration: `Source/NXPlanet/NXPlanetView.h:1517`, `Source/NXPlanet/NXPlanetView.h:1539`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1055`, `Source/NXPlanet/NXPlanetView.cpp:1060`

## ChangeLayerOrder
- Description: 렌더 레이어의 순서를 바꿔준다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:768`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1986`

## ClearLayer
- Description: 뷰에 연결된 모든 레이어를 삭제한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:242`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:212`

## GeographicToScreen
- Description: 위경도 좌표를 스크린 좌표로 변환한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:640`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:911`

## GeographicToWorld
- Description: 위경도 좌표를 세계 좌표로 변환한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:661`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:933`

## GetCameraState
- Description: 현재 카메라의 상태를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:559`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:674`

## GetDrawArgs
- Description: PlanetView 컨트롤 및 렌더링 정보가 담긴 Draw argument를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1647`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2315`

## GetFreezeViewArea
- Description: 뷰의 고정여부를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1874`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:870`

## GetHandle
- Description: 뷰의 컨트롤 핸들을 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:463`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:259`

## GetIndexMapMode
- Description: 인덱스 맵 모드를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1866`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:856`

## GetLayer
- Description: 렌더 레이어를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:780`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2030`

## GetLayerOrder
- Description: 현재 렌더 레이어의 순서를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:775`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2002`

## GetMapAlitutdeFromCADRGScale
- Description: CADRG 축척을 기준으로 카메라 높이를 계산한다. CADRG NS PixelSize와의 비율로 해상도를 계산하고 이에 대한 카메라 높이를 반환한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:482`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1127`

## GetMapAltitude
- Description: 입력 축척에 대응하는 카메라의 높이를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:472`, `Source/NXPlanet/NXPlanetView.h:477`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1093`, `Source/NXPlanet/NXPlanetView.cpp:1121`

## GetMouseControlMode
- Description: 마우스 제어 상태를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:808`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2064`

## GetPTMOverlayLayer
- Description: Planet의 지형 관리자로부터 중첩 레이어(NXOverlayLayer)를 가져온다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:763`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1977`

## GetWOS
- Description: 뷰의 WOS를 가져온다( World offset and Scale).
- Declaration: `Source/NXPlanet/NXPlanetView.h:467`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:659`

## IsUnderMouse
- Description: 마우스아래 뷰가 있는지 확인한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1857`
- Implementation: `not found`

## LookTarget
- Description: 바라보는 위치와 거리, 방위각과 고도 값에 의해 현재 카메라 상태를 설정한다. [Planet 3D뷰를 위함]
- Declaration: `Source/NXPlanet/NXPlanetView.h:608`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:835`

## MaxZoomIn
- Description: 고도를 통해 최대 줌인을 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1559`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2097`

## MaxZoomOut
- Description: 고도를 통해 최대 줌 아웃을 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1567`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2112`

## RefreshBaseMap
- Description: 특정 위치와 해상도에 대한 기본 배경 지도를 갱신 요청한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:680`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:642`

## RefreshLOD
- Description: LOD를 기반으로 화면을 갱신하여 도시하도록 요청한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:674`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:634`

## RefreshScreen
- Description: 화면을 갱신하여 도시하도록 요청한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:670`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:616`

## Release
- Description: 뷰에 연결된 엔진과 갈무리 버퍼의 연결을 끊고 모든 레이어를 삭제한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:240`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:193`

## RemoveRenderLayer
- Description: 뷰에 레이어를 분리한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:541`, `Source/NXPlanet/NXPlanetView.h:551`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:972`, `Source/NXPlanet/NXPlanetView.cpp:984`

## RequestRender
- Description: 새로 렌더링을 요청한다. 카메라 설정 등을 바꾸고 요청 식별자를 특정해서 부를 수 있다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:684`, `Source/NXPlanet/NXPlanetView.h:689`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:649`, `Source/NXPlanet/NXPlanetView.cpp:654`

## ScreenToGeographic
- Description: 스크린 좌표를 위경도 좌표로 변환한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:635`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:902`

## ScreenToWorld
- Description: 스크린 좌표를 세계 좌표로 변환한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:646`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:878`

## SetCameraPosition
- Description: 현재 카메라의 상태를 눈의 위치와 방위각에 의해 설정하며, 기본 기울기의 값은 0 이다 [Planet 2D뷰를 위함]
- Declaration: `Source/NXPlanet/NXPlanetView.h:570`, `Source/NXPlanet/NXPlanetView.h:578`, `Source/NXPlanet/NXPlanetView.h:587`, `Source/NXPlanet/NXPlanetView.h:593`, `Source/NXPlanet/NXPlanetView.h:600`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:751`, `Source/NXPlanet/NXPlanetView.cpp:767`, `Source/NXPlanet/NXPlanetView.cpp:784`, `Source/NXPlanet/NXPlanetView.cpp:801`, `Source/NXPlanet/NXPlanetView.cpp:818`

## SetCameraState
- Description: 현재 카메라의 상태를 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:564`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:711`

## SetEarthShow
- Description: 지구 레이어를 표시 또는 숨기기 여부를 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:666`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:609`

## SetFreezeViewArea
- Description: 뷰를 고정시킬지 여부를 설정한다
- Declaration: `Source/NXPlanet/NXPlanetView.h:1870`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:863`

## SetIndexMapMode
- Description: 인덱스 맵 모드를 설정한다
- Declaration: `Source/NXPlanet/NXPlanetView.h:1862`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:849`

## SetLightingFactor
- Description: 빛 효과를 위한 주변광, 분사광(diffuse), 반사광(specular) 비율을 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1643`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2309`

## SetMouseControlMode
- Description: 확대축소, 회전, 이동의 마우스 제어 상태를 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:804`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2057`

## SetPBEDefaultDataSet
- Description: 새로운 PBE 데이터 소스를 설정한다. 기존에 이용하는 PBE 데이터는 삭제되고 새로운 데이터를 로딩하여 도시한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:699`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1176`

## SetPBIDefaultDataSet
- Description: 새로운 PBI 데이터 소스를 설정한다. 기존에 도시되는 PBI 데이터는 삭제되고 새로운 데이터를 로딩하여 도시한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:694`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1134`

## SetPBPDefaultDataSet
- Description: 새로운 PBP 데이터 소스를 설정한다. 기존에 도시되는 PBP 데이터는 삭제되고 새로운 데이터를 로딩하여 도시한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:704`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1234`

## SetPBVDefaultDataSet
- Description: 새로운 PBV 데이터 소스를 설정한다. 기존에 도시되는 PBV 데이터는 삭제되고 새로운 데이터를 로딩하여 도시한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:733`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1336`

## SetRenderArea
- Description: 화면에 렌더링되는 영역을 설정한다. Planet2D 모드에서만 적용된다. RestrictRenderArea를 참으로 설정하면 이 함수를 통해 설정된 값으로 렌더링 영역이 제한된다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1575`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1912`

## SetRenderSkip
- Description: 렌더링 주기를 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1878`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2208`

## SetSunFollowCamera
- Description: 태양의 위치를 카메라의 위치와 동일하게 설정할지를 설정한다. Planet3D 모드에서만 지원
- Declaration: `Source/NXPlanet/NXPlanetView.h:1628`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2249`

## SetSunPosition
- Description: 대기 효과(밤/낮)를 위한 태양의 위치를 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1592`, `Source/NXPlanet/NXPlanetView.h:1611`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2230`, `Source/NXPlanet/NXPlanetView.cpp:2239`

## SetViewZoomCenterPosition
- Description: 해당 좌표를 기준으로 마우스 휠 줌을 한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:1551`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:2072`

## SetWorkSpaceHgt
- Description: 카메라의 높이 구간을 설정한다
- Declaration: `Source/NXPlanet/NXPlanetView.h:626`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1957`

## SetWorkSpaceLat
- Description: 카메라의 위도 구간을 설정한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:620`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1939`

## SetWorkSpaceLon
- Description: 카메라의 경도 구간을 설정한다
- Declaration: `Source/NXPlanet/NXPlanetView.h:614`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1921`

## UpdatePBPDataSet
- Description: PBP 데이터소스를 갱신한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:728`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1273`

## UpdatePBVDataSet
- Description: PBV 데이터소스를 갱신한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:757`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:1379`

## WorldToGeographic
- Description: 세계 좌표를 위경도 좌표로 변환한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:656`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:922`

## WorldToScreen
- Description: 세계 좌표를 스크린 좌표로 변환한다.
- Declaration: `Source/NXPlanet/NXPlanetView.h:651`
- Implementation: `Source/NXPlanet/NXPlanetView.cpp:890`
