---
title: Raster Enhance Workflow
aliases:
  - Raster Enhance Workflow
  - wf-raster-enhance
  - wf raster enhance
symbols:
  - XDMComposite
  - eCompCutType
  - eCompStretchCoverage
  - eCompStretchType
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Tune cut and stretch parameters for display quality.
- Core calls:
  - `XDMComposite.SetCutType`
  - `XDMComposite.SetStretchCoverage`
  - `XDMComposite.SetStretchType`
  - `XDMComposite.SetCutMin`
  - `XDMComposite.SetCutMax`
- Verified source:
  - `Source/NXDLrs/NXDLrs.h:1445`
  - `Source/NXDLrs/NXDLrs.h:1455`
  - `Source/NXDLrs/NXDLrs.h:1465`
  - `Source/NXDLrs/NXDLrs.h:1477`
  - `Source/NXDLrs/NXDLrs.h:1487`
- Steps:
  - 기존 Composite를 유지한다.
  - cut/stretch 설정을 조정한다.
  - 수동 min/max는 마지막에만 사용한다.


## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XDMComposite.SetCutType
  - XDMComposite.SetStretchCoverage
  - XDMComposite.SetStretchType
  - XDMComposite.SetCutMin
  - XDMComposite.SetCutMax
required_facts:
  - symbol: XDMComposite.SetCutType
    declaration: 'void		SetCutType(eCompCutType CutType, int Idx);'
    source: 'Source/NXDLrs/NXDLrs.h:1445'
  - symbol: XDMComposite.SetStretchCoverage
    declaration: 'void		SetStretchCoverage(eCompStretchCoverage StretchCoverage, int Idx);'
    source: 'Source/NXDLrs/NXDLrs.h:1477'
  - symbol: XDMComposite.SetStretchType
    declaration: 'void		SetStretchType(eCompStretchType StretchType, int Idx);'
    source: 'Source/NXDLrs/NXDLrs.h:1487'
  - symbol: XDMComposite.SetCutMin
    declaration: 'void		SetCutMin(double min, int Idx);'
    source: 'Source/NXDLrs/NXDLrs.h:1455'
  - symbol: XDMComposite.SetCutMax
    declaration: 'void		SetCutMax(double max, int Idx);'
    source: 'Source/NXDLrs/NXDLrs.h:1465'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
