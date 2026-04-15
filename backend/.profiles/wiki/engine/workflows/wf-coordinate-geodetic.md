---
title: Geodetic Utility Workflow
aliases:
  - Geodetic Utility Workflow
  - wf-coordinate-geodetic
  - wf coordinate geodetic
symbols:
  - Xcc
  - Xfn
  - XGeoPoint
  - XAngle
  - XVertex3d
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Use geodetic helper functions for distance, angle, area, and geo/ecr conversion.
- Core calls:
  - `Xcc.CalcGeodeticDistance`
  - `Xcc.CalcGeodeticAngle`
  - `Xcc.CalcGeodeticArea`
  - `Xcc.ConvPixelSize`
  - `Xfn.GeoToEcr`
  - `Xfn.EcrToGeo`
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:551`
  - `Source/NXDLcc/NXDLcc.h:563`
  - `Source/NXDLcc/NXDLcc.h:635`
  - `Source/NXDLcc/NXDLcc.h:640`
  - `Source/NXDL/NXDL.h:3658`
  - `Source/NXDL/NXDL.h:3675`
- Steps:
  - 물리 질문의 종류를 먼저 정한다.
  - XAngle/XGeoPoint 기준으로 입력을 유지한다.
  - 필요한 지오데틱 유틸을 호출한다.


## Required Facts
```yaml
workflow_family: coordinate
output_shape: focused_snippet_or_helper
required_symbols:
  - Xcc.CalcGeodeticDistance
  - Xcc.CalcGeodeticAngle
  - Xcc.CalcGeodeticArea
  - Xcc.ConvPixelSize
  - Xfn.GeoToEcr
  - Xfn.EcrToGeo
required_facts:
  - symbol: Xcc.CalcGeodeticDistance
    declaration: 'static double CalcGeodeticDistance(NXDL::XAngle^ lon1, NXDL::XAngle^ lat1, NXDL::XAngle^ lon2, NXDL::XAngle^ lat2);'
    source: 'Source/NXDLcc/NXDLcc.h:551'
  - symbol: Xcc.CalcGeodeticAngle
    declaration: 'static double CalcGeodeticAngle(NXDL::XAngle^ lonCenter, NXDL::XAngle^ latCenter, NXDL::XAngle^ lon1, NXDL::XAngle^ lat1, NXDL::XAngle^ lon2, NXDL::XAngle^ lat2);'
    source: 'Source/NXDLcc/NXDLcc.h:563'
  - symbol: Xcc.CalcGeodeticArea
    declaration: 'static double CalcGeodeticArea(cli::array<XGeoPoint^>^ vertArray);'
    source: 'Source/NXDLcc/NXDLcc.h:640'
  - symbol: Xcc.ConvPixelSize
    declaration: 'static void ConvPixelSize(XSpatialReference^ SrIn, XSpatialReference^ SrOut, double latReference, double lonReference, double% pixelSizeX, double% pixelSizeY);'
    source: 'Source/NXDLcc/NXDLcc.h:635'
  - symbol: Xfn.GeoToEcr
    declaration: 'static void		GeoToEcr(XGeoPoint^ geo, XVertex3d^% ecr);'
    source: 'Source/NXDL/NXDL.h:3658'
  - symbol: Xfn.EcrToGeo
    declaration: 'static void		EcrToGeo(XVertex3d^ ecr, XGeoPoint^% geo);'
    source: 'Source/NXDL/NXDL.h:3675'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
