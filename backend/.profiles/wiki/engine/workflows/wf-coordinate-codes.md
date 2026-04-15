---
title: Coordinate Code Workflow
aliases:
  - Coordinate Code Workflow
  - wf-coordinate-codes
  - wf coordinate codes
symbols:
  - Xcc
  - XAngle
  - XVertex2d
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Convert between WGS84, UTM, MGRS, and GEOREF.
- Core calls:
  - `Xcc.WGP2UTM`
  - `Xcc.UTM2WGP`
  - `Xcc.WGP2MGRS`
  - `Xcc.MGRS2UTM`
  - `Xcc.MGRS2WGP`
  - `Xcc.WGP2GEOREF`
  - `Xcc.GEOREF2WGP`
- Verified source:
  - `Source/NXDLcc/NXDLcc.h:340`
  - `Source/NXDLcc/NXDLcc.h:344`
  - `Source/NXDLcc/NXDLcc.h:370`
  - `Source/NXDLcc/NXDLcc.h:397`
  - `Source/NXDLcc/NXDLcc.h:419`
  - `Source/NXDLcc/NXDLcc.h:464`
  - `Source/NXDLcc/NXDLcc.h:522`
  - `Source/NXDLcc/NXDLcc.h:541`
  - `Source/NXDLcc/NXDLcc.h:587`
  - `Source/NXDLcc/NXDLcc.h:605`
- Steps:
  - WGS84 lon/lat 입력을 준비한다.
  - 대상 코드 체계를 고른다.
  - 필요 시 역변환 함수를 사용한다.


## Required Facts
```yaml
workflow_family: coordinate
output_shape: focused_snippet_or_helper
required_symbols:
  - Xcc.WGP2UTM
  - Xcc.UTM2WGP
  - Xcc.WGP2MGRS
  - Xcc.MGRS2UTM
  - Xcc.MGRS2WGP
  - Xcc.WGP2GEOREF
  - Xcc.GEOREF2WGP
required_facts:
  - symbol: Xcc.WGP2UTM
    declaration_candidates:
      - declaration: 'static bool WGP2UTM(NXDL::XAngle^ lon, NXDL::XAngle^ lat, NXDL::XVertex2d^% pos, int% Zone);'
        source: 'Source/NXDLcc/NXDLcc.h:344'
      - declaration: 'static bool WGP2UTM(NXDL::XAngle^ lon, NXDL::XAngle^ lat, NXDL::XVertex2d^% pos, int% Zone, String^% latitudeBand);'
        source: 'Source/NXDLcc/NXDLcc.h:370'
      - declaration: 'static bool WGP2UTM(NXDL::XAngle^ lon, NXDL::XAngle^ lat, NXDL::XVertex2d^% pos, int% Zone, bool ForceApplyZone);'
        source: 'Source/NXDLcc/NXDLcc.h:397'
  - symbol: Xcc.UTM2WGP
    declaration: 'static bool UTM2WGP(NXDL::XVertex2d^ pos, int Zone, NXDL::XAngle^% lon, NXDL::XAngle^% lat);'
    source: 'Source/NXDLcc/NXDLcc.h:464'
  - symbol: Xcc.WGP2MGRS
    declaration_candidates:
      - declaration: 'static bool WGP2MGRS(NXDL::XAngle^ lon, NXDL::XAngle^ lat, String^% strMGRS);'
        source: 'Source/NXDLcc/NXDLcc.h:419'
      - declaration: 'static bool WGP2MGRS(NXDL::XAngle^ lon, NXDL::XAngle^ lat, String^% strMGRS, int precision);'
        source: 'Source/NXDLcc/NXDLcc.h:442'
  - symbol: Xcc.MGRS2UTM
    declaration: 'static bool MGRS2UTM(String^ strMGRS, NXDL::XVertex2d^% pos, int% Zone);'
    source: 'Source/NXDLcc/NXDLcc.h:522'
  - symbol: Xcc.MGRS2WGP
    declaration: 'static bool MGRS2WGP(String^ strMGRS, NXDL::XAngle^% lon, NXDL::XAngle^% lat);'
    source: 'Source/NXDLcc/NXDLcc.h:541'
  - symbol: Xcc.WGP2GEOREF
    declaration: 'static bool WGP2GEOREF(NXDL::XAngle^ lon, NXDL::XAngle^ lat, int% numDigit, String^% strGEOREF);'
    source: 'Source/NXDLcc/NXDLcc.h:587'
  - symbol: Xcc.GEOREF2WGP
    declaration: 'static bool GEOREF2WGP(String^ strGEOREF, NXDL::XAngle^% lon, NXDL::XAngle^% lat);'
    source: 'Source/NXDLcc/NXDLcc.h:605'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
