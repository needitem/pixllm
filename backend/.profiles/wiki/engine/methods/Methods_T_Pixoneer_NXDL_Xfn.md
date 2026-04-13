---
title: Pixoneer.NXDL.Xfn Methods
aliases:
  - Xfn Methods
  - Pixoneer.NXDL.Xfn
  - Xfn
symbols:
  - Xfn
  - CalArcDistAndAngle
  - CalcAzimuthElevationOfTarget
  - CalcEulerAngleZYXOfFrame
  - CalcGlobalModelAttitude
  - CalcGlobalSensorAttitudeInPlatform
  - CalcGlobalSensorAttitudeInPlatformAxis3
  - CalcGlobalSensorAttitudeInPlatformUAS
  - CalcPosByBearingAndDist
  - CalcRelativeSensorAttitudeInPlatformUAS
  - Close
  - DotProduct
  - EcrToGeo
  - ELUToYPR
  - GeoToEcr
  - GetConfigPath
  - GetDataSize
  - GetDataTypeString
  - GetDocumentPath
  - GetFrameENU
  - GetFrameNED
  - GetLastErrorMsg
  - GetModelTransform
  - GetResourcePath
  - GetScaleFactor
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `Xfn`
- HTML source: `html/Methods_T_Pixoneer_NXDL_Xfn.htm`
- Type declaration: `Source/NXDL/NXDL.h:3214`
- Method count: `41`

## CalArcDistAndAngle
- Description: 두 위도/경도 점을 입력하여 두 점 간의 거리와 방향(첫 번째 점으로부터 두 번째 점을 잇는 선분에 대한 북쪽으로의 방향)을 계산한다.
- Declaration: `Source/NXDL/NXDL.h:3404`
- Implementation: `Source/NXDL/NXDL.cpp:1274`, `Source/NXDL/NXDL.cpp:1278`, `Source/NXDLMilSymbol/reference/DrawOverItem.cpp:109`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3041`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4004`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4079`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4104`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4180`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4205`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4229`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4337`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5870`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5931`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5962`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6014`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6043`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6071`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6136`

## CalcAzimuthElevationOfTarget
- Description: 방위각과 고도방위각도를 계산한다.
- Declaration: `Source/NXDL/NXDL.h:3431`
- Implementation: `Source/NXDL/NXDL.cpp:1287`, `Source/NXDL/NXDL.cpp:1304`

## CalcEulerAngleZYXOfFrame
- Description: 두 좌표계 간 오일러 회전각을 구한다. 기준 좌표계의 좌표축 vXref, vYref, vZref를 각각 X, Y, Z축이라고 할 때, Z축 기준으로 yaw만큼, 회전된 Y축 기준으로 pitch만큼, 다시 회전된 X축 기준으로 roll만큼 회전하면 최종 회전된 X, Y, Z축이 주어진 좌표계의 X축(vXfrm), Y축(vYfrm), Z축(vZfrm)과 일치하는 오일러 회전각 yaw, pitch, roll을 구한다.
- Declaration: `Source/NXDL/NXDL.h:3622`
- Implementation: `Source/NXDL/NXDL.cpp:1412`, `Source/NXDL/NXDL.cpp:1442`, `Source/NXDL/NXDL.cpp:1465`, `Source/NXDL/NXDL.cpp:1475`

## CalcGlobalModelAttitude
- Description: 로컬 좌표계에서 만든 모델을 지구 타원체 상의 특정 지점에 위치하도록 하는 자세를 구한다. 모델 자체의 회전이 없다면, NED 좌표축에서 N축을 모델 좌표계의 Y축, E축을 X축, D축을 -Z축과 나란히 하는 자세각을 구하여, 모델을 이 자세로 회전하면 모델의 원점 좌표를 주어진 지리 좌표에 두고 모델의 XY 평면이 그 점의 접평면이 되게 하고 Z축이 지상 위로 향하도록 자세를 잡는다. 모델 좌표축에 대한 회전각을 입력하면 주어진 지상점을 원점으로 하고 회전이 반영된 모델 자세를 구한다.
- Declaration: `Source/NXDL/NXDL.h:3568`, `Source/NXDL/NXDL.h:3588`
- Implementation: `Source/NXDL/NXDL.cpp:1397`, `Source/NXDL/NXDL.cpp:1420`

## CalcGlobalSensorAttitudeInPlatform
- Description: 지구 타원체 상의 특정 지점에서 지구 중심으로 향하는 축과 직교하는 좌표계(ENU)에 대하여 기체의 회전값 yawPlatform, pitchPlatform, rollPlatform을 입력으로 받아 기체에 장착된 2축 카메라 짐벌 회전을 고려하여 카메라가 지향하는 yaw, pitch, roll값을 계산한다. 즉, 기체의 회전요소와 카메라의 회전요소를 결합하여 특정 지점에서의 카메라의 회전 각도를 계산해 낸다.
- Declaration: `Source/NXDL/NXDL.h:3469`
- Implementation: `Source/NXDL/NXDL.cpp:1325`, `Source/NXDL/NXDL.cpp:1328`, `Source/NXVideo/XVideoEncoder.cpp:845`

## CalcGlobalSensorAttitudeInPlatformAxis3
- Description: 지구 타원체 상의 특정 지점에서 지구 중심으로 향하는 축과 직교하는 좌표계(ENU)에 대하여 기체의 회전값 yawPlatform, pitchPlatform, rollPlatform을 입력으로 받아 기체에 장착된 3축 카메라 짐벌 회전을 고려하여 카메라가 지향하는 yaw, pitch, roll값을 계산한다. 즉, 기체의 회전 요소와 카메라의 회전 요소를 결합하여 특정 지점에서의 카메라의 회전 각도를 계산해 낸다.
- Declaration: `Source/NXDL/NXDL.h:3487`
- Implementation: `Source/NXDL/NXDL.cpp:1337`, `Source/NXDL/NXDL.cpp:1340`, `Source/NXVideo/XVideoEncoder.cpp:848`

## CalcGlobalSensorAttitudeInPlatformUAS
- Description: UAS LS 표준에 따라 지구 타원체 상의 특정 지점에서 지구 중심으로 향하는 축과 직교하는 좌표계(NED)에서 North 시선 방향인 기체와 센서의 회전각을 입력 받아서 D 방향을 지향하는 센서가 탑재된 N 방향 기준의 센서 자세를 나타내는 yaw, pitch, roll값을 계산한다. 즉, 입력 지점에서 NED 축을 입력된 자세로 회전했을 때 센서의 시선은 N축과 일치하고, 센서의 시선이 D축으로 정렬되는 자세 회전각을 계산한다.
- Declaration: `Source/NXDL/NXDL.h:3506`
- Implementation: `Source/NXDL/NXDL.cpp:1349`, `Source/NXDL/NXDL.cpp:1352`

## CalcPosByBearingAndDist
- Description: 특정 위치(위경도)에서 북쪽으로부터 bearing값과 거리에 해당하는 위도, 경도값을 계산한다.
- Declaration: `Source/NXDL/NXDL.h:3373`
- Implementation: `Source/NXDL/NXDL.cpp:1263`, `Source/NXDL/NXDL.cpp:1266`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3793`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3799`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3805`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:3811`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4007`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4013`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4019`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4025`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4049`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4082`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4087`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4092`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4097`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4107`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4112`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4117`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4122`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4148`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4183`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4188`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4193`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4198`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4207`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4212`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4217`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4222`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4232`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4237`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4242`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4247`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4300`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4340`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4346`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4352`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4358`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4364`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:4370`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5873`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5877`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5881`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5885`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5935`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5939`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5943`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5947`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5965`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5969`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5973`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5977`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6017`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6021`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6025`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6029`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6045`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6049`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6053`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6057`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6074`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6078`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6082`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6086`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6140`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6145`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6154`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6159`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6167`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:6172`

## CalcRelativeSensorAttitudeInPlatformUAS
- Description: UAS LS 표준에 따라 지구 타원체 상의 특정 지점에서 지구 중심으로 향하는 축과 직교하는 좌표계(NED)에서 North 시선 방향인 기체와 센서의 회전각을 입력받아서 기체 자세에 상대적인 센서의 자세 회전각을 계산한다.
- Declaration: `Source/NXDL/NXDL.h:3521`
- Implementation: `Source/NXDL/NXDL.cpp:1362`, `Source/NXDL/NXDL.cpp:1365`, `Source/NXVideo/XVideoEncoder.cpp:861`

## Close
- Description: 엔진에서 사용중인 메모리 리소스 등을 모두 반환한다. 이 함수는 응용 프로그램이 종료되기 전에 호출되어야 메모리 누수를 방지할 수 있다. 간혹 응용 프로그램 창이 열려있는 것과 같이 NXDL 외부에서 이벤트 핸들러가 남아있는 경우가 있다. 이런 경우 접근 오류가 발생하므로 입력 플래그를 두어 명시적으로 응용 프로그램의 모든 창을 닫을 수 있도록 한다.
- Declaration: `Source/NXDL/NXDL.h:3311`, `Source/NXDL/NXDL.h:3317`
- Implementation: `Source/NXDL/NXDL.cpp:880`, `Source/NXDL/NXDL.cpp:988`

## DotProduct
- Description: 두 개의 XVertex3d 객체를 이용하여 Dot product를 계산하고 결과값을 Scalar값으로 반환한다.
- Declaration: `Source/NXDL/NXDL.h:3630`
- Implementation: `Source/NXDL/NXDL.cpp:1526`, `Source/NXDL/NXDL.cpp:1531`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:395`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:445`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:476`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:507`

## EcrToGeo
- Description: ECEF 좌표를 위경도 좌표로 변환한다.
- Declaration: `Source/NXDL/NXDL.h:3675`
- Implementation: `Source/NXDL/NXDL.cpp:1567`, `Source/NXDL/NXDL.cpp:1570`

## ELUToYPR
- Description: ECEF 공간 상에서 카메라 위치/업 벡터, 대상 위치를 이용하여 카메라의 자세(Yaw, Pitch, roll)을 계산한다.
- Declaration: `Source/NXDL/NXDL.h:3718`
- Implementation: `Source/NXDL/NXDL.cpp:1515`, `Source/NXDL/NXDL.cpp:1518`

## GeoToEcr
- Description: 위경도 좌표로부터 ECEF좌표로 변환한다.
- Declaration: `Source/NXDL/NXDL.h:3658`
- Implementation: `Source/NXDL/NXDL.cpp:1559`, `Source/NXDL/NXDL.cpp:1561`, `Source/NXDLMilSymbol/reference/XscMilSymbol.cpp:1190`

## GetConfigPath
- Description: Planet에서 사용하는 XDLConfigration.xml 파일이 있는 경로를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:3244`
- Implementation: `Source/NXDL/NXDL.cpp:1012`

## GetDataSize
- Description: eDataType의 데이터 크기(Byte 수)를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:3226`
- Implementation: `Source/NXDL/NXDL.cpp:58`, `Source/NXDL/NXDL.cpp:60`, `Source/NXDL/XGrid.cpp:166`

## GetDataTypeString
- Description: eDataType의 데이터 형식을 문자열로 반환한다.
- Declaration: `Source/NXDL/NXDL.h:3221`
- Implementation: `Source/NXDL/NXDL.cpp:20`, `Source/NXDL/NXDL.h:3221`

## GetDocumentPath
- Description: XDL의 Document 폴더 경로를 얻는다.
- Declaration: `Source/NXDL/NXDL.h:3267`
- Implementation: `Source/NXDL/NXDL.cpp:1028`, `Source/NXDL/NXDL.cpp:1030`

## GetFrameENU
- Description: ECEF 공간 위치에서 지구 중심에 대한 ENU 방향 벡터를 계산한다.
- Declaration: `Source/NXDL/NXDL.h:3693`
- Implementation: `Source/NXDL/NXDL.cpp:1407`, `Source/NXDL/NXDL.cpp:1430`, `Source/NXDL/NXDL.cpp:1493`, `Source/NXDL/NXDL.cpp:1498`

## GetFrameNED
- Description: ECEF 공간 위치에서 지구 중심에 대한 NED 방향 벡터를 계산한다.
- Declaration: `Source/NXDL/NXDL.h:3684`
- Implementation: `Source/NXDL/NXDL.cpp:1480`, `Source/NXDL/NXDL.cpp:1485`, `Source/NXDL/NXDL.cpp:1667`

## GetLastErrorMsg
- Description: XDL의 마지막 오류 문자열을 반환한다.
- Declaration: `Source/NXDL/NXDL.h:3288`
- Implementation: `Source/NXDL/NXDL.cpp:1066`

## GetModelTransform
- Description: 모델의 지리좌표, 자세 회전각과 3차원 배율로부터 모델 좌표를 지리좌표로 변환하는 4x4 변환행렬을 구한다.
- Declaration: `Source/NXDL/NXDL.h:3730`, `Source/NXDL/NXDL.h:3741`
- Implementation: `Source/NXDL/NXDL.cpp:1651`, `Source/NXDL/NXDL.cpp:1656`

## GetResourcePath
- Description: 리소스가 존재하는 상위 폴더의 경로를 얻는다.
- Declaration: `Source/NXDL/NXDL.h:3263`
- Implementation: `Source/NXDL/NXDL.cpp:1021`, `Source/NXDL/NXDL.cpp:1023`, `Source/NXDLwnd/ChangePropertyDialog.cpp:18`, `Source/NXDLwnd/CoordinateSelector.cpp:39`

## GetScaleFactor
- Description: 입력되는 상수값으로 부터 선형 방정식에 대한 scale factor를 계산한다. Linear equation A = sf0 + sf1 * a; B = sf0 + sf1 * b;
- Declaration: `Source/NXDL/NXDL.h:3753`, `Source/NXDL/NXDL.h:3765`
- Implementation: `Source/NXDL/NXDL.cpp:1243`, `Source/NXDL/NXDL.cpp:1247`, `Source/NXDL/NXDL.cpp:1253`, `Source/NXDL/NXDL.cpp:1257`

## GetSensorPointingVector
- Description: 지구 타원체 상의 특정 지점에서 지구 중심으로 향하는 축과 직교하는 좌표계(ENU)에 대한 각 축의 성분 벡터와 그 좌표계로부터 회전값 yaw, pitch, roll을 적용하여 이루어진 ECEF공간상의 방향 벡터를 계산한다. 위성 등의 움직입을 고려할 때, Z축 성분은 지구 중심, Y축 성분은 속도의 반대 방향, X축 성분은 YxZ 방향을 가진다.
- Declaration: `Source/NXDL/NXDL.h:3451`
- Implementation: `Source/NXDL/NXDL.cpp:1309`, `Source/NXDL/NXDL.cpp:1320`

## GetSPTargetOnWGS84ByDist
- Description: 센서로 부터 거리 dist만큼 떨어진 WGS84 타원체 상에 특정 입사각에 해당하는 타겟의 위치를 얻는다.
- Declaration: `Source/NXDL/NXDL.h:3345`
- Implementation: `Source/NXDL/NXDL.cpp:1209`

## GetTempPathA
- Description: XDL의 임시 파일 관리 경로를 얻는다.
- Declaration: `not found`
- Implementation: `not found`

## IntersectLineAndEarth
- Description: ECEF 좌표계에서 두 점(PosS, PosE)을 연장하는 직선이 지구(WGS84)와 만나는 점을 구한다.
- Declaration: `Source/NXDL/NXDL.h:3815`
- Implementation: `Source/NXDL/NXDL.cpp:1713`, `Source/NXDL/NXDL.cpp:1720`

## IntersectLookAndEarth
- Description: ECEF 좌표계에서 한 점(Pos)와 Look 방향으로 진행하는 직선을 연장하였을 때, 이 직선이 지구(WGS84)와 만나는 점을 구한다.
- Declaration: `Source/NXDL/NXDL.h:3828`
- Implementation: `Source/NXDL/NXDL.cpp:1738`, `Source/NXDL/NXDL.cpp:1745`

## IsDataTypeComplex
- Description: 데이터 형식이 복소수형(complex)인지 확인한다.
- Declaration: `Source/NXDL/NXDL.h:3231`
- Implementation: `Source/NXDL/NXDL.cpp:63`, `Source/NXDL/NXDL.cpp:65`, `Source/NXDLrs/XDMBandComplex.cpp:83`

## IsValidLicense
- Description: XDL 라이선스가 유효한지 확인한다.
- Declaration: `Source/NXDL/NXDL.h:3284`
- Implementation: `Source/NXDL/NXDL.cpp:1047`, `Source/NXDL/NXDL.cpp:1050`, `Source/NXDL/NXDL.cpp:1054`

## MergeChannels
- Description: XGrid 형식의 데이터를 하나의 BGR 또는 RGB 형식의 XGrid 데이터로 합친다. 입력 데이터는 크기(Column/Row 크기)는 동일해야 하고 1 바이트크기의 동일한 데이터형식이어야 한다.
- Declaration: `Source/NXDL/NXDL.h:3778`
- Implementation: `Source/NXDL/NXDL.cpp:1575`

## OmegaPhiKappaToYawPitchRoll
- Description: 투영 좌표계 원점의 ENU 좌표계를 기준으로 하는 카메라 회전각 omega, phi, kappa에 해당하는 센서 위치의 yaw, pitch, roll을 계산한다.
- Declaration: `Source/NXDL/NXDL.h:3536`
- Implementation: `Source/NXDL/NXDL.cpp:1373`, `Source/NXDL/NXDL.cpp:1376`

## PolyFit
- Description: 입력 x에 대한 y값을 계산하는 y = f(x)에 대하여, 함수 f()를 사용자가 설정한 차수(degree)의 다항함수로 추정하여 그 계수를 제공한다. 최소제곱법(least square approximation)을 사용. degree = 3 일 때 Xfn.PolyFit(x, y, 3, coeff); 3차 다항식 : y = a + b*x + c*x^2 + d*x^3 계수 : coeff[0] = a, coeff[1] = b, coeff[2] = c, coeff[3] = d
- Declaration: `Source/NXDL/NXDL.h:3803`
- Implementation: `Source/NXDL/NXDL.cpp:1687`

## RotateFrame
- Description: 서로 수직인 세 기저벡터로 주어진 좌표축을 주어진 각도로 순서대로 회전시킨 새 좌표축을 얻는다. 회전 순서는 vAxis1 방향축을 기준으로 ang1 각도로 회전시킨 후, vAxis2 방향축이 회전한 축을 기준으로 ang2 각도만큼 회전시키고, 다시 vAxis3 방향축이 회전한 축을 기준으로 ang3 각도만큼 회전시킨다. 회전각은 오른손 법칙을 따라 부호를 결정한다. (회전축 방향으로 바라볼 때 시계 방향이 양의 방향이다.)
- Declaration: `Source/NXDL/NXDL.h:3605`
- Implementation: `Source/NXDL/NXDL.cpp:1409`, `Source/NXDL/NXDL.cpp:1439`, `Source/NXDL/NXDL.cpp:1450`, `Source/NXDL/NXDL.cpp:1459`, `Source/NXDL/NXDL.cpp:1668`

## SetConfigPath
- Description: Planet에서 사용하는 XDLConfigration.xml 파일이 있는 경로를 설정한다.
- Declaration: `Source/NXDL/NXDL.h:3238`
- Implementation: `Source/NXDL/NXDL.cpp:1003`

## SplitChannel
- Description: BGR 또는 RGB 형식의 XGrid 데이터를 각각의 요소로 분리하여 XGrid로 생성한다.
- Declaration: `Source/NXDL/NXDL.h:3788`
- Implementation: `Source/NXDL/NXDL.cpp:1615`

## SVD
- Description: Singular Value Decomposition
- Declaration: `Source/NXDL/NXDL.h:3640`
- Implementation: `Source/NXDL/NXDL.cpp:1534`

## ValidateLicense
- Description: XDL 라이선스가 유효한지 확인한다.
- Declaration: `Source/NXDL/NXDL.h:3276`
- Implementation: `Source/NXDL/NXDL.cpp:1042`

## YawPitchRollToOmegaPhiKappa
- Description: 센서 자세를 투영 좌표계 원점의 ENU 좌표계를 기준으로 하는 카메라 회전각 omega, phi, kappa로 변환한다.
- Declaration: `Source/NXDL/NXDL.h:3551`
- Implementation: `Source/NXDL/NXDL.cpp:1385`, `Source/NXDL/NXDL.cpp:1388`

## YPRToELU
- Description: ECEF 공간 상에서 카메라 위치/자세(Yaw, Pitch, roll), 대상과의 거리를 입력하여 대상위치(LookAt) 및 Up 벡터를 계산한다.
- Declaration: `Source/NXDL/NXDL.h:3706`
- Implementation: `Source/NXDL/NXDL.cpp:1505`, `Source/NXDL/NXDL.cpp:1508`
