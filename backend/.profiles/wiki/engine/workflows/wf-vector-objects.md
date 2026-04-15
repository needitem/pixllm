---
title: Vector Objects Workflow
aliases:
  - Vector Objects Workflow
  - wf-vector-objects
  - wf vector objects
symbols:
  - XvcObj
  - XvcPoint
  - XvcLine
  - XvcPolyline
  - XvcPolygon
  - XvcLayer
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Create vector geometry, inspect attributes, and hit-test vector layers.
- Core calls:
  - `XvcObj.GetPropertyNameAt`
  - `XvcObj.GetPropertyValueAt`
  - `XvcPoint.Add`
  - `XvcLine.Add`
  - `XvcPolyline.Add`
  - `XvcPolygon.Add`
  - `XvcLayer.HitTest`
- Verified source:
  - `Source/NXDLvc/NXDLvc.h:233`
  - `Source/NXDLvc/NXDLvc.h:234`
  - `Source/NXDLvc/NXDLvc.h:349`
  - `Source/NXDLvc/NXDLvc.h:354`
  - `Source/NXDLvc/NXDLvc.h:452`
  - `Source/NXDLvc/NXDLvc.h:508`
  - `Source/NXDLvc/NXDLvc.h:572`
  - `Source/NXDLvc/NXDLvc.h:644`
  - `Source/NXDLvc/NXDLvc.h:1341`
  - `Source/NXDLvc/NXDLvc.h:1515`
- Steps:
  - 객체를 로드하거나 생성한다.
  - 속성은 property API로 읽는다.
  - 지오메트리는 Add 계열로 구성한다.
  - 선택/탐색은 HitTest로 처리한다.


## Required Facts
```yaml
workflow_family: scene_or_vector
output_shape: workflow_bound_to_host_context
required_symbols:
  - XvcObj.GetPropertyNameAt
  - XvcObj.GetPropertyValueAt
  - XvcPoint.Add
  - XvcLine.Add
  - XvcPolyline.Add
  - XvcPolygon.Add
  - XvcLayer.HitTest
required_facts:
  - symbol: XvcObj.GetPropertyNameAt
    declaration: 'String^ GetPropertyNameAt(int idx);'
    source: 'Source/NXDLvc/NXDLvc.h:354'
  - symbol: XvcObj.GetPropertyValueAt
    declaration: 'String^ GetPropertyValueAt(int idx);'
    source: 'Source/NXDLvc/NXDLvc.h:349'
  - symbol: XvcPoint.Add
    declaration_candidates:
      - declaration: 'int			Add(XVertex3d^ vt);'
        source: 'Source/NXDLvc/NXDLvc.h:452'
      - declaration: 'int			Add(double x, double y, double z);'
        source: 'Source/NXDLvc/NXDLvc.h:459'
      - declaration: 'int			Add(XVertex3d^ vt);'
        source: 'Source/NXDLvc/NXDLvc.h:508'
      - declaration: 'int			Add(double x, double y, double z);'
        source: 'Source/NXDLvc/NXDLvc.h:515'
      - declaration: 'int			Add(XVertex3d^ vt);'
        source: 'Source/NXDLvc/NXDLvc.h:572'
      - declaration: 'int			Add(XVertex3d^ vt);'
        source: 'Source/NXDLvc/NXDLvc.h:644'
  - symbol: XvcLine.Add
    declaration_candidates:
      - declaration: 'int			Add(XVertex3d^ vt);'
        source: 'Source/NXDLvc/NXDLvc.h:452'
      - declaration: 'int			Add(double x, double y, double z);'
        source: 'Source/NXDLvc/NXDLvc.h:459'
      - declaration: 'int			Add(XVertex3d^ vt);'
        source: 'Source/NXDLvc/NXDLvc.h:508'
      - declaration: 'int			Add(double x, double y, double z);'
        source: 'Source/NXDLvc/NXDLvc.h:515'
      - declaration: 'int			Add(XVertex3d^ vt);'
        source: 'Source/NXDLvc/NXDLvc.h:572'
      - declaration: 'int			Add(XVertex3d^ vt);'
        source: 'Source/NXDLvc/NXDLvc.h:644'
  - symbol: XvcPolyline.Add
    declaration_candidates:
      - declaration: 'int			Add(XVertex3d^ vt);'
        source: 'Source/NXDLvc/NXDLvc.h:452'
      - declaration: 'int			Add(double x, double y, double z);'
        source: 'Source/NXDLvc/NXDLvc.h:459'
  - symbol: XvcPolygon.Add
    declaration_candidates:
      - declaration: 'int			Add(XVertex3d^ vt);'
        source: 'Source/NXDLvc/NXDLvc.h:508'
      - declaration: 'int			Add(double x, double y, double z);'
        source: 'Source/NXDLvc/NXDLvc.h:515'
  - symbol: XvcLayer.HitTest
    declaration: 'virtual XvcObj^	HitTest(XVertex3d^ vt, double wppx, double wppy, XHitFlag^% hit);'
    source: 'Source/NXDLvc/NXDLvc.h:362'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
