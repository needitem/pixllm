---
title: Pixoneer.NXDL.NXPlanet.NXMapTileGenerator Methods
aliases:
  - NXMapTileGenerator Methods
  - Pixoneer.NXDL.NXPlanet.NXMapTileGenerator
  - NXMapTileGenerator
symbols:
  - NXMapTileGenerator
  - Dispose
  - GenerateTile
  - LoadElevation
  - SetConfigurationPath
  - SetPBEDefaultDatSet
  - SetPBIDefaultDataSet
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nxplanet
---

# Overview
- Namespace: `Pixoneer.NXDL.NXPlanet`
- Type: `NXMapTileGenerator`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXPlanet_NXMapTileGenerator.htm`
- Type declaration: `Source/NXPlanet/NXMapTileGenerator.h:20`
- Method count: `6`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXPlanet.NXMapTileGenerator
type_name: NXMapTileGenerator
namespace: Pixoneer.NXDL.NXPlanet
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
## Dispose
- Description: No description in HTML reference.
- Declaration: `not found`
- Implementation: `not found`

## GenerateTile
- Description: PBI 기반 지도에서 입력 영역을 읽어 특정 크기의 타일 이미지를 생성하여 저장한다.
- Declaration: `Source/NXPlanet/NXMapTileGenerator.h:62`
- Implementation: `Source/NXPlanet/NXMapTileGenerator.cpp:125`

## LoadElevation
- Description: PBE 기반 고도에서 입력 영역을 읽어 특정 크기의 고도 데이터를 반환한다. 출력 데이터형식의 유효값 영역으로 잘라서 생성한다.
- Declaration: `Source/NXPlanet/NXMapTileGenerator.h:76`
- Implementation: `Source/NXPlanet/NXMapTileGenerator.cpp:292`

## SetConfigurationPath
- Description: 배경지도 데이터세트 설정파일 경로를 설정한다.
- Declaration: `Source/NXPlanet/NXMapTileGenerator.h:40`
- Implementation: `Source/NXPlanet/NXMapTileGenerator.cpp:94`

## SetPBEDefaultDatSet
- Description: 배경지도의 기본 고도 데이터세트를 설정한다.
- Declaration: `Source/NXPlanet/NXMapTileGenerator.h:48`
- Implementation: `Source/NXPlanet/NXMapTileGenerator.cpp:114`

## SetPBIDefaultDataSet
- Description: 배경지도의 기본 데이터세트를 설정한다.
- Declaration: `Source/NXPlanet/NXMapTileGenerator.h:44`
- Implementation: `Source/NXPlanet/NXMapTileGenerator.cpp:104`
