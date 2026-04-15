---
title: Pixoneer.NXDL.NDFS.XPBIProviderGroup Methods
aliases:
  - XPBIProviderGroup Methods
  - Pixoneer.NXDL.NDFS.XPBIProviderGroup
  - XPBIProviderGroup
symbols:
  - XPBIProviderGroup
  - AddPBIFile
  - AddXDMCompManager
  - Clear
  - IsTextureUsable
  - LoadTile
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - ndfs
---

# Overview
- Namespace: `Pixoneer.NXDL.NDFS`
- Type: `XPBIProviderGroup`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NDFS_XPBIProviderGroup.htm`
- Type declaration: `Source/NXDLdfs/NXDLdfs.h:70`
- Method count: `5`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NDFS.XPBIProviderGroup
type_name: XPBIProviderGroup
namespace: Pixoneer.NXDL.NDFS
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
## AddPBIFile
- Description: Planet에 지형 영상 서비스를 위하여 PBI파일을 추가한다. PBI 파일을 strProviderName이 다르면 내부적으로 다른 파일 그룹을 생성한다. 일단 파일 그룹이 생성되면 입력된 파일명에 해당하는 PBI파일을 해당 그룹으로 추가한다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:88`
- Implementation: `Source/NXDLdfs/XPBIProvider.cpp:46`

## AddXDMCompManager
- Description: Planet에 지형 영상 서비스를 위하여 XDMCompManager를 추가한다. XDMCompManager객체는 주로 ImageView에서 영상을 도시하기 위해서 사용하며 XDMComposite객체를 포함하고 있어서 해당영역에 해당하는 지형자료를 서비스 가능하다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:95`
- Implementation: `Source/NXDLdfs/XPBIProvider.cpp:64`

## Clear
- Description: 객체의 모든 리소스들을 삭제시킨다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:81`
- Implementation: `Source/NXDLdfs/XPBIProvider.cpp:40`

## IsTextureUsable
- Description: 입력되는 level, row, col 타일에 대한 PBI가 유용한지 여부를 확인해서 반환한다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:115`
- Implementation: `Source/NXDLdfs/XPBIProvider.cpp:99`

## LoadTile
- Description: 입력되는 level, row, col 타일에 대한 PBI를 로딩하여 비트맵을 생성한다.
- Declaration: `Source/NXDLdfs/NXDLdfs.h:122`
- Implementation: `Source/NXDLdfs/XPBIProvider.cpp:104`
