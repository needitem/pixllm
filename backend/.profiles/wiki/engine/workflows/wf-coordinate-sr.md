---
title: Spatial Reference Workflow
aliases:
  - Spatial Reference Workflow
  - wf-coordinate-sr
  - wf coordinate sr
symbols:
  - XSpatialReference
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Create and inspect spatial references before transforming points.
- Core calls:
  - `XSpatialReference.SetWellKnownGeogCS`
  - `XSpatialReference.IsGeographic`
  - `XSpatialReference.IsProjected`
  - `XSpatialReference.IsUTM`
  - `XSpatialReference.GetUTMZone`
  - `XSpatialReference.IsSame`
  - `XSpatialReference.GetAreaOfUse`
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:152`
  - `Source/NXDLcc/NXDLcc.h:156`
  - `Source/NXDLcc/NXDLcc.h:170`
  - `Source/NXDLcc/NXDLcc.h:183`
  - `Source/NXDLcc/NXDLcc.h:194`
  - `Source/NXDLcc/NXDLcc.h:198`
  - `Source/NXDLcc/NXDLcc.h:213`
- Steps:
  - 입력/출력 SR을 먼저 만든다.
  - 좌표계 타입과 UTM 여부를 확인한다.
  - 필요 시 적용 범위를 확인한다.


## Required Facts
```yaml
workflow_family: coordinate
output_shape: focused_snippet_or_helper
required_symbols:
  - XSpatialReference.SetWellKnownGeogCS
  - XSpatialReference.IsGeographic
  - XSpatialReference.IsProjected
  - XSpatialReference.IsUTM
  - XSpatialReference.GetUTMZone
  - XSpatialReference.IsSame
  - XSpatialReference.GetAreaOfUse
required_facts:
  - symbol: XSpatialReference.SetWellKnownGeogCS
    declaration: 'void	SetWellKnownGeogCS(String^ strGeog);'
    source: 'Source/NXDLcc/NXDLcc.h:183'
  - symbol: XSpatialReference.IsGeographic
    declaration: 'bool	IsGeographic();'
    source: 'Source/NXDLcc/NXDLcc.h:152'
  - symbol: XSpatialReference.IsProjected
    declaration: 'bool	IsProjected();'
    source: 'Source/NXDLcc/NXDLcc.h:156'
  - symbol: XSpatialReference.IsUTM
    declaration: 'bool	IsUTM();'
    source: 'Source/NXDLcc/NXDLcc.h:198'
  - symbol: XSpatialReference.GetUTMZone
    declaration: 'int		GetUTMZone(bool% bNorth);'
    source: 'Source/NXDLcc/NXDLcc.h:194'
  - symbol: XSpatialReference.IsSame
    declaration: 'bool	IsSame(XSpatialReference^ sr);'
    source: 'Source/NXDLcc/NXDLcc.h:170'
  - symbol: XSpatialReference.GetAreaOfUse
    declaration: 'bool	GetAreaOfUse(double% westLon, double% southLat, double% eastLon, double% northLat, String^% strAreaName);'
    source: 'Source/NXDLcc/NXDLcc.h:213'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
