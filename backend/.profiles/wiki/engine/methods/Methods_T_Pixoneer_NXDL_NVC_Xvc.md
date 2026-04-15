---
title: Pixoneer.NXDL.NVC.Xvc Methods
aliases:
  - Xvc Methods
  - Pixoneer.NXDL.NVC.Xvc
  - Xvc
symbols:
  - Xvc
  - CalcAngle
  - CalcAreaFromVertexes
  - CalcDistance
  - CreateCastedXvcObj
  - CreateCloneObj
  - ParsingNITFCGM
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nvc
---

# Overview
- Namespace: `Pixoneer.NXDL.NVC`
- Type: `Xvc`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NVC_Xvc.htm`
- Type declaration: `Source/NXDLvc/NXDLvc.h:1604`
- Method count: `6`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NVC.Xvc
type_name: Xvc
namespace: Pixoneer.NXDL.NVC
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
## CalcAngle
- Description: 두 선 사이의 각도를 계산한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1631`
- Implementation: `Source/NXDLvc/NXDLvc.cpp:680`

## CalcAreaFromVertexes
- Description: 정점 배열로 이루어지는 영역을 계산한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1618`
- Implementation: `Source/NXDLvc/NXDLvc.cpp:634`

## CalcDistance
- Description: 두 점 사이의 거리를 계산한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1624`
- Implementation: `Source/NXDLvc/NXDLvc.cpp:660`

## CreateCastedXvcObj
- Description: VC::XvcObj C++로 캐스팅된 객체를 생성한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1609`
- Implementation: `Source/NXDLrsEx/XDMBandFeatureExt.cpp:133`, `Source/NXDLrsEx/XDMBandMosaicLT.cpp:111`, `Source/NXDLrsEx/XDMBandMosaicLT.cpp:129`, `Source/NXDLrsEx/XDMBandMosaicLT.cpp:147`, `Source/NXDLvc/NXDLvc.cpp:484`, `Source/NXDLvc/NXDLvc.cpp:553`, `Source/NXDLvc/NXDLvc.cpp:628`, `Source/NXDLvc/XvcBase.cpp:199`, `Source/NXDLvc/XvcBase.cpp:221`, `Source/NXDLvc/XvcGroup.cpp:46`, `Source/NXDLvc/XvcLayer.cpp:161`, `Source/NXDLvc/XvcLayer.cpp:181`, `Source/NXDLvc/XvcText.cpp:144`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:182`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:183`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:206`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:227`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:236`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:245`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:259`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:274`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:309`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:316`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:324`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:331`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:338`, `Source/NXImage/NXImageLayerStereoVectorEditor.cpp:345`, `Source/NXImage/NXImageLayerVectorDisplay.cpp:102`, `Source/NXImage/NXImageLayerVectorEditor.cpp:177`, `Source/NXImage/NXImageLayerVectorEditor.cpp:207`, `Source/NXImage/NXImageLayerVectorEditor.cpp:229`, `Source/NXImage/NXImageLayerVectorEditor.cpp:238`, `Source/NXImage/NXImageLayerVectorEditor.cpp:252`, `Source/NXImage/NXImageLayerVectorEditor.cpp:313`, `Source/NXImage/NXImageLayerVectorEditor.cpp:320`, `Source/NXImage/NXImageLayerVectorEditor.cpp:327`, `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:169`, `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:192`, `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:201`, `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:222`, `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:229`, `Source/NXPlanet/NXPlanetLayerVectorEditor.cpp:236`

## CreateCloneObj
- Description: 특정 객체와 동일한 객체를 생성한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1613`
- Implementation: `Source/NXDLvc/NXDLvc.cpp:620`

## ParsingNITFCGM
- Description: NITF(National Imagery Transmission Format) CGM(Computer Graphics Metafile) 데이터를 파싱하여 새로운 XvcLayer를 생성한다.
- Declaration: `Source/NXDLvc/NXDLvc.h:1637`
- Implementation: `Source/NXDLvc/NXDLvc.cpp:686`, `Source/NXDLvc/NXDLvc.cpp:702`
