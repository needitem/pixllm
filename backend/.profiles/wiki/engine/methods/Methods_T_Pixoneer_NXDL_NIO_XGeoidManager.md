---
title: Pixoneer.NXDL.NIO.XGeoidManager Methods
aliases:
  - XGeoidManager Methods
  - Pixoneer.NXDL.NIO.XGeoidManager
  - XGeoidManager
symbols:
  - XGeoidManager
  - GetXSize
  - GetYSize
  - LoadFileFromEGM2008
  - PixelToWorld
  - ReadPixel
  - SetEGMType
  - WorldToPixel
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nio
---

# Overview
- Namespace: `Pixoneer.NXDL.NIO`
- Type: `XGeoidManager`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NIO_XGeoidManager.htm`
- Type declaration: `Source/NXDLio/NXDLio.h:1002`
- Method count: `7`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NIO.XGeoidManager
type_name: XGeoidManager
namespace: Pixoneer.NXDL.NIO
method_section_prefix: "## "
verification_rules:
  - treat_declaration_lines_as_symbol_existence_evidence
  - treat_implementation_lines_as_source_anchor_evidence
  - prefer_this_page_over_examples_for_exact_call_shapes
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page to verify exact symbol existence before emitting code.
- Cross-check declaration and implementation lines when overloads or call shapes matter.
- Treat examples and workflow pages as composition guidance, but treat this page as the canonical member list.
## GetXSize
- Description: X축(가로방향) 크기를 얻는다.
- Declaration: `Source/NXDLio/NXDLio.h:1045`
- Implementation: `Source/NXDLio/XGeoidManager.cpp:76`

## GetYSize
- Description: Y축(세로방향) 크기를 얻는다.
- Declaration: `Source/NXDLio/NXDLio.h:1049`
- Implementation: `Source/NXDLio/XGeoidManager.cpp:81`

## LoadFileFromEGM2008
- Description: EGM2008 파일을 로딩한다.
- Declaration: `Source/NXDLio/NXDLio.h:1016`
- Implementation: `Source/NXDLio/XGeoidManager.cpp:40`

## PixelToWorld
- Description: 화소 좌표(Grid상의 Sample/Line 위치)를 위경도 좌표로 변환한다.
- Declaration: `Source/NXDLio/NXDLio.h:1034`
- Implementation: `Source/NXDLio/XGeoidManager.cpp:60`

## ReadPixel
- Description: 입력 위경도 좌표에 대한 Geoid값을 bilinear 리샘플링하여 반환한다.
- Declaration: `Source/NXDLio/NXDLio.h:1022`, `Source/NXDLio/NXDLio.h:1027`
- Implementation: `Source/NXDLio/XGeoidManager.cpp:50`, `Source/NXDLio/XGeoidManager.cpp:55`

## SetEGMType
- Description: EGM 형식을 설정한다.
- Declaration: `Source/NXDLio/NXDLio.h:1053`
- Implementation: `Source/NXDLio/XGeoidManager.cpp:86`

## WorldToPixel
- Description: 위경도 좌표를 화소 좌표(Grid상의 Sample/Line 위치)로 변환한다.
- Declaration: `Source/NXDLio/NXDLio.h:1041`
- Implementation: `Source/NXDLio/XGeoidManager.cpp:68`
