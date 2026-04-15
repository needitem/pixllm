---
title: Pixoneer.NXDL.XGeoPoint Methods
aliases:
  - XGeoPoint Methods
  - Pixoneer.NXDL.XGeoPoint
  - XGeoPoint
symbols:
  - XGeoPoint
  - FromAngle
  - FromDegree
  - FromEcr
  - FromEec
  - FromRadian
  - FromWM
  - IsEqual
  - llh
  - llhd
  - llhr
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `XGeoPoint`
- HTML source: `html/Methods_T_Pixoneer_NXDL_XGeoPoint.htm`
- Type declaration: `Source/NXDL/NXDL.h:1542`
- Method count: `10`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.XGeoPoint
type_name: XGeoPoint
namespace: Pixoneer.NXDL
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
## FromAngle
- Description: XAngle객체인 위도, 경도, 고도 값을 입력 받아 XGeoPoint객체를 생성하여 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1577`
- Implementation: `Source/NXDL/XGeoPoint.cpp:70`

## FromDegree
- Description: double 형의 위도, 경도, 고도 값을 Degree값으로 입력 받아 XGeoPoint객체를 생성하여 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1595`
- Implementation: `Source/NXDL/XGeoPoint.cpp:84`, `Source/NXDLcc/NXDLcc.cpp:94`, `Source/NXDLdfs/XPBEProviderExporter.cpp:125`, `Source/NXDLdfs/XPBEProviderExporter.cpp:126`, `Source/NXDLdfs/XPBIProviderExporter.cpp:80`, `Source/NXDLdfs/XPBIProviderExporter.cpp:81`, `Source/NXDLio/XRPFToc.cpp:97`, `Source/NXDLio/XRPFToc.cpp:98`, `Source/NXDLio/XRPFToc.cpp:99`, `Source/NXDLio/XRPFToc.cpp:100`, `Source/NXDLMilSymbol/reference/DrawOverItem.cpp:122`, `Source/NXDLMilSymbol/reference/DrawOverItem.cpp:123`, `Source/NXDLMilSymbol/reference/DrawOverItem.cpp:1625`, `Source/NXDLMilSymbol/reference/DrawOverItem.cpp:1883`, `Source/NXDLMilSymbol/reference/DrawOverItem.cpp:1901`, `Source/NXDLMilSymbol/reference/ICOPSSymbolView.cpp:590`, `Source/NXDLMilSymbol/reference/ICOPSSymbolView.cpp:604`, `Source/NXDLMilSymbol/reference/ICOPSSymbolView.cpp:618`, `Source/NXDLMilSymbol/reference/ICOPSSymbolView.cpp:632`, `Source/NXDLMilSymbol/reference/XDLProjection.cpp:191`, `Source/NXDLMilSymbol/reference/XDLProjection.cpp:206`, `Source/NXDLMilSymbol/reference/XDLProjection.cpp:220`, `Source/NXDLMilSymbol/reference/XDLProjection.cpp:299`, `Source/NXDLMilSymbol/reference/XscMilSymbol.cpp:1155`, `Source/NXDLMilSymbol/reference/XscMilSymbol.cpp:1170`, `Source/NXDLMilSymbol/reference/XscMilSymbol.cpp:1183`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5411`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5412`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5413`, `Source/NXDLMilSymbol/reference_ex/SymbolObj.cpp:5414`, `Source/NXDLMilSymbol/XMilSymbolLayer.cpp:512`, `Source/NXDLMilSymbol/XMilSymbolLayer.cpp:513`, `Source/NXDLrs/XRSFile.cpp:314`, `Source/NXDLrs/XRSFile.cpp:317`, `Source/NXDLrs/XRSFile.cpp:320`, `Source/NXDLrs/XRSFile.cpp:323`, `Source/NXImage/NXImageView.cpp:909`, `Source/NXImage/NXImageView.cpp:910`, `Source/NXVideo/XFrameMetad.cpp:283`, `Source/NXVideo/XFrameMetad.cpp:303`

## FromEcr
- Description: ECR 좌표 값을 XVertex3d 객체로 입력 받아 XGeoPoint 객체를 생성하여 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1602`, `Source/NXDL/NXDL.h:1611`
- Implementation: `Source/NXDL/XGeoPoint.cpp:91`, `Source/NXDL/XGeoPoint.cpp:98`, `Source/NXDL/XGeoPoint.cpp:280`, `Source/NXDLMilSymbol/reference/XDLProjection.cpp:248`, `Source/NXDLMilSymbol/reference/XscMilSymbol.cpp:1211`, `Source/NXDLsm/XMIG.cpp:58`, `Source/NXDLsm/XMIG.cpp:80`, `Source/NXDLsm/XMIG.cpp:89`, `Source/NXVideo/XVideoEncoder.cpp:819`, `Source/NXVideo/XVideoEncoder.cpp:820`

## FromEec
- Description: XVertex3d형의 EEC좌표계 값을 입력 받아 XGeoPoint값으로 변환한다.
- Declaration: `Source/NXDL/NXDL.h:1618`, `Source/NXDL/NXDL.h:1627`
- Implementation: `Source/NXDL/XGeoPoint.cpp:105`, `Source/NXDL/XGeoPoint.cpp:112`, `Source/NXDL/XGeoPoint.cpp:304`, `Source/NXDLMilSymbol/reference/ICOPSSymbolView.cpp:732`, `Source/NXDLMilSymbol/reference/ICOPSSymbolView.cpp:733`, `Source/NXDLMilSymbol/reference/XDLProjection.cpp:261`, `Source/NXDLMilSymbol/reference/XscMilSymbol.cpp:1224`

## FromRadian
- Description: double 형의 위도, 경도, 고도 값을 Radian값으로 입력 받아 XGeoPoint객체를 생성하여 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1586`
- Implementation: `Source/NXDL/XGeoPoint.cpp:77`, `Source/NXDL/XGeoPoint.cpp:238`, `Source/NXDL/XGeoPoint.cpp:357`

## FromWM
- Description: XVertex3d형의 Web Mercator좌표계 값을 입력 받아 XGeoPoint값으로 변환한다.
- Declaration: `Source/NXDL/NXDL.h:1634`, `Source/NXDL/NXDL.h:1643`
- Implementation: `Source/NXDL/XGeoPoint.cpp:119`, `Source/NXDL/XGeoPoint.cpp:126`, `Source/NXDL/XGeoPoint.cpp:328`, `Source/NXDLMilSymbol/reference/ICOPSSymbolView.cpp:744`, `Source/NXDLMilSymbol/reference/ICOPSSymbolView.cpp:745`, `Source/NXDLMilSymbol/reference/XDLProjection.cpp:274`, `Source/NXDLMilSymbol/reference/XDLProjection.cpp:331`, `Source/NXDLMilSymbol/reference/XscMilSymbol.cpp:1236`, `Source/NXImage/NXImageView.cpp:899`, `Source/NXImage/NXImageView.cpp:900`

## IsEqual
- Description: 입력된 XGeoPoint객체의 값과 동일한지 여부를 확인하여 같을 경우 true를, 다르면 false를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:1706`
- Implementation: `Source/NXDL/XGeoPoint.cpp:344`

## llh
- Description: XAngle객체의 위도, 경도와 double형의 고도값(단위 Meter)으로 객체의 값을 설정한다.
- Declaration: `Source/NXDL/NXDL.h:1663`
- Implementation: `Source/NXDL/XGeoPoint.cpp:230`

## llhd
- Description: 경도, 위도와 고도값을 XVertex3d의 x, y, z값으로 변경하여 반환한다. 이 때 x, y값의 단위는 Degree이고 z값은 Meter이다.
- Declaration: `Source/NXDL/NXDL.h:1649`, `Source/NXDL/NXDL.h:1671`
- Implementation: `Source/NXDL/XGeoPoint.cpp:169`, `Source/NXDL/XGeoPoint.cpp:256`

## llhr
- Description: 객체의 경도, 위도와 고도값을 XVertex3d의 x, y, z값으로 변경하여 반환한다. 이 때 x, y값의 단위는 Radian이고 z값은 Meter이다.
- Declaration: `Source/NXDL/NXDL.h:1655`, `Source/NXDL/NXDL.h:1679`
- Implementation: `Source/NXDL/XGeoPoint.cpp:174`, `Source/NXDL/XGeoPoint.cpp:264`
