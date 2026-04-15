---
title: Pixoneer.NXDL.NXMilmap.NXMilmapConfig Methods
aliases:
  - NXMilmapConfig Methods
  - Pixoneer.NXDL.NXMilmap.NXMilmapConfig
  - NXMilmapConfig
symbols:
  - NXMilmapConfig
  - Add
  - AddFDBMapLayerDefinition
  - GetFDBMapLayerDefinitionAt
  - GetIdx
  - GetMapScaleAt
  - GetNumberOfFDBMapLayerDefinition
  - GetNumOfMapScales
  - GetNumOfPBPScales
  - GetPBPScaleAt
  - Load
  - Remove
  - RemoveMapScaleAt
  - RemovePBPScaleAt
  - Save
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nxmilmap
---

# Overview
- Namespace: `Pixoneer.NXDL.NXMilmap`
- Type: `NXMilmapConfig`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXMilmap_NXMilmapConfig.htm`
- Type declaration: `Source/NXMilmap/NXMilmapConfig.h:214`
- Method count: `14`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXMilmap.NXMilmapConfig
type_name: NXMilmapConfig
namespace: Pixoneer.NXDL.NXMilmap
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
## Add
- Description: MilmapScale을 추가한다. MilmapScale 종류에 따라 MapScales와 PBPScales에 추가한다.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:230`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:910`

## AddFDBMapLayerDefinition
- Description: FDB 지도 축척/종류별 레이어 정의 파일 경로를 키워드와 함께 추가한다.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:316`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:1053`

## GetFDBMapLayerDefinitionAt
- Description: FDB 지도 축척/종류별 레이어 정의 파일의 키워드와 파일 경로(XML 형식)를 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:311`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:1031`

## GetIdx
- Description: 입력 MilmapScale에 대한 인덱스를 가져온다. MilmapScale 종류에 따라 해당 목록에 대한 인덱스를 반환한다.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:260`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:972`

## GetMapScaleAt
- Description: 인덱스 위치의 지도 MilmapScale을 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:250`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:954`

## GetNumberOfFDBMapLayerDefinition
- Description: FDB 지도 축척/종류별 레이어 정의자료의 개수를 반환한다.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:303`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:1022`

## GetNumOfMapScales
- Description: 지도 축척의 개수를 가져온다. MapScales 그룹으로 정의되는 지도 축척.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:264`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:986`

## GetNumOfPBPScales
- Description: 지명 데이터 그룹의 개수를 가져온다. PBPScales 그룹으로 정의되는 지명 그룹.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:268`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:994`

## GetPBPScaleAt
- Description: 인덱스 위치의 지명데이터 MilmapScale을 가져온다.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:255`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:963`

## Load
- Description: NXMilmap 환경설정을 로딩한다.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:220`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:360`

## Remove
- Description: 매개변수 MilmapScale을 제거한다. MilmapScale 종류에 따라 MapScales와 PBPScales 목록에서 제거한다.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:235`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:920`

## RemoveMapScaleAt
- Description: 인덱스 위치에 있는 지도 MilmapScale을 제거한다.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:240`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:930`

## RemovePBPScaleAt
- Description: 인덱스 위치에 있는 지명데이터 MilmapScale을 제거한다.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:245`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:942`

## Save
- Description: NXMilmap 환경설정을 저장한다.
- Declaration: `Source/NXMilmap/NXMilmapConfig.h:225`
- Implementation: `Source/NXMilmap/NXMilmapConfig.cpp:887`
