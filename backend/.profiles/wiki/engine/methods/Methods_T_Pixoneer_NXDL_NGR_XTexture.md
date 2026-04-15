---
title: Pixoneer.NXDL.NGR.XTexture Methods
aliases:
  - XTexture Methods
  - Pixoneer.NXDL.NGR.XTexture
  - XTexture
symbols:
  - XTexture
  - Bind
  - FreeTextureInDevice
  - GetRGBA
  - Load
  - SendTextureToDevice
  - Set
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - ngr
---

# Overview
- Namespace: `Pixoneer.NXDL.NGR`
- Type: `XTexture`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NGR_XTexture.htm`
- Type declaration: `Source/NXDLgr/XTexture.h:82`
- Method count: `6`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NGR.XTexture
type_name: XTexture
namespace: Pixoneer.NXDL.NGR
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
## Bind
- Description: 텍스처 객체를 OpenGL에 바인딩한다.
- Declaration: `Source/NXDLgr/XTexture.h:385`
- Implementation: `Source/NXDLgr/XTexture.cpp:255`

## FreeTextureInDevice
- Description: 디바이스(그래픽 카드)에서 관리되고 있는 텍스처를 삭제한다.
- Declaration: `Source/NXDLgr/XTexture.h:381`
- Implementation: `Source/NXDLgr/XTexture.cpp:240`

## GetRGBA
- Description: 입력 문자열에 대한 텍스쳐 데이터를 RGBA 형식으로 로딩한다. 파일 형태 또는 키워드를 이용한 텍스처 로딩을 할 수 있다.
- Declaration: `Source/NXDLgr/XTexture.h:373`
- Implementation: `Source/NXDLgr/XTexture.cpp:172`

## Load
- Description: 파일 경로(PNG, BMP, JPG등 파일) 또는 텍스처 키워드(TextureDriver를 활용할 때)를 이용하여 텍스처 데이터를 로딩한다.
- Declaration: `Source/NXDLgr/XTexture.h:105`
- Implementation: `Source/NXDLgr/XTexture.cpp:89`

## SendTextureToDevice
- Description: 이 객체를 디바이스(그래픽 카드)에서 사용할 수 있도록 한다.
- Declaration: `Source/NXDLgr/XTexture.h:377`
- Implementation: `Source/NXDLgr/XTexture.cpp:224`

## Set
- Description: 32 비트형 비트맵 데이터를 XTexture 객체에 설정한다.
- Declaration: `Source/NXDLgr/XTexture.h:365`
- Implementation: `Source/NXDLgr/XTexture.cpp:130`
