---
title: Coordinate Transform Workflow
aliases:
  - Coordinate Transform Workflow
  - wf-coordinate-transform
  - wf coordinate transform
symbols:
  - XCoordinateTransformation
  - XSpatialReference
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Build a reusable coordinate transformation from two SRs.
- Core calls:
  - `XCoordinateTransformation.CreateCoordinateTransform`
  - `XCoordinateTransformation.TransformPt`
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:265`
  - `Source/NXDLcc/NXDLcc.h:269`
  - `Source/NXDLcc/NXDLcc.h:291`
  - `Source/NXDLcc/NXDLcc.h:301`
  - `Source/NXDLcc/NXDLcc.h:309`
- Steps:
  - 입력/출력 SR을 준비한다.
  - 변환기를 생성한다.
  - TransformPt를 반복 호출한다.


## Required Facts
```yaml
workflow_family: coordinate
output_shape: focused_snippet_or_helper
required_symbols:
  - XCoordinateTransformation.CreateCoordinateTransform
  - XCoordinateTransformation.TransformPt
required_facts:
  - symbol: XCoordinateTransformation.CreateCoordinateTransform
    declaration: 'bool CreateCoordinateTransform(XSpatialReference^% SrIn, XSpatialReference^% SrOut);'
    source: 'Source/NXDLcc/NXDLcc.h:291'
  - symbol: XCoordinateTransformation.TransformPt
    declaration_candidates:
      - declaration: 'bool TransformPt(double xIn, double yIn, double% xOut, double% yOut);'
        source: 'Source/NXDLcc/NXDLcc.h:301'
      - declaration: 'bool TransformPt(double% x, double% y);'
        source: 'Source/NXDLcc/NXDLcc.h:309'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
