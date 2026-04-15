---
title: Pixoneer.NXDL.NIO.XRasterIO Methods
aliases:
  - XRasterIO Methods
  - Pixoneer.NXDL.NIO.XRasterIO
  - XRasterIO
symbols:
  - XRasterIO
  - CreateImagePyramid
  - DumpFile
  - DumpMeta
  - Export
  - ExportComposites
  - GetDriverKey
  - GetFileInfo
  - GetFiltersForLoad
  - GetFiltersForSave
  - GetSubDatasets
  - Initialize
  - IsExtensionExportSupported
  - IsExtensionImportSupported
  - IsKeyImportSupported
  - LoadFile
  - LoadRawFile
  - SetConfigOption
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
- Type: `XRasterIO`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NIO_XRasterIO.htm`
- Type declaration: `Source/NXDLio/NXDLio.h:187`
- Method count: `17`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NIO.XRasterIO
type_name: XRasterIO
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
## CreateImagePyramid
- Description: 영상 피라미드(오버뷰)를 생성한다.
- Declaration: `Source/NXDLio/NXDLio.h:748`
- Implementation: `Source/NXDLio/XRasterIO.cpp:794`

## DumpFile
- Description: 영상 파일의 이미지와 메타데이터를 다른 영상 파일 형식과 xml 파일로 각각 저장한다. 출력 파일 경로를 "C:\abc.tif"로 설정시 abc.tif와 abc.xml로 영상과 메타정보가 저장된다. 입력 영상 파일 포맷이 HDF5일 경우, 각 DataSet별로 영상 파일로 저장되고 메타정보는 하나의 xml 파일로 저장된다.
- Declaration: `Source/NXDLio/NXDLio.h:538`
- Implementation: `Source/NXDLio/XRasterIO.cpp:265`

## DumpMeta
- Description: 영상 파일의 메타 정보를 xml로 저장한다.
- Declaration: `Source/NXDLio/NXDLio.h:548`
- Implementation: `Source/NXDLio/XRasterIO.cpp:379`

## Export
- Description: 여러 개의 밴드가 있는 XRSSaveFile 객체를 임의의 파일 형식으로 저장한다.
- Declaration: `Source/NXDLio/NXDLio.h:584`, `Source/NXDLio/NXDLio.h:595`, `Source/NXDLio/NXDLio.h:612`
- Implementation: `Source/NXDLio/XRasterIO.cpp:565`, `Source/NXDLio/XRasterIO.cpp:609`, `Source/NXDLio/XRasterIO.cpp:647`

## ExportComposites
- Description: 여러 개의 XDMComposite를 포함하는 XDMCompManager 객체를 출력 조건을 설정하여 파일로 저장한다.
- Declaration: `Source/NXDLio/NXDLio.h:631`, `Source/NXDLio/NXDLio.h:650`
- Implementation: `Source/NXDLio/XRasterIO.cpp:683`, `Source/NXDLio/XRasterIO.cpp:736`

## GetDriverKey
- Description: 입력 인덱스에 의한 Driver 키워드를 반환한다.
- Declaration: `Source/NXDLio/NXDLio.h:665`
- Implementation: `Source/NXDLio/XRasterIO.cpp:973`

## GetFileInfo
- Description: 표준 및 상용 포맷의 이미지 파일 정보를 로딩한다.
- Declaration: `Source/NXDLio/NXDLio.h:568`, `Source/NXDLio/NXDLio.h:575`
- Implementation: `Source/NXDLio/XRasterIO.cpp:406`, `Source/NXDLio/XRasterIO.cpp:430`

## GetFiltersForLoad
- Description: XRasterIO객체로부터 로딩이 가능한 필터를 얻는다. 이 필터 문자열은 열기 대화상자 등에서 사용할 수 있다.
- Declaration: `Source/NXDLio/NXDLio.h:655`
- Implementation: `Source/NXDLio/XRasterIO.cpp:862`

## GetFiltersForSave
- Description: XRasterIO객체로부터 저장이 가능한 필터를 얻는다. 이 필터 문자열은 저장 대화상자 등에서 사용할 수 있다.
- Declaration: `Source/NXDLio/NXDLio.h:660`
- Implementation: `Source/NXDLio/XRasterIO.cpp:939`

## GetSubDatasets
- Description: 파일의 하위 데이터 집합이 있는 경우 데이터 집합 문자열을 가져온다.
- Declaration: `Source/NXDLio/NXDLio.h:340`
- Implementation: `Source/NXDLio/XRasterIO.cpp:236`

## Initialize
- Description: 객체를 초기화하고 IO 드라이버를 로딩한다.
- Declaration: `Source/NXDLio/NXDLio.h:198`
- Implementation: `Source/NXDLio/XRasterIO.cpp:72`

## IsExtensionExportSupported
- Description: 파일 확장자에 대응하는 파일 저장(export, save)이 지원되는지 확인한다.
- Declaration: `Source/NXDLio/NXDLio.h:208`
- Implementation: `Source/NXDLio/XRasterIO.cpp:107`

## IsExtensionImportSupported
- Description: 파일 확장자에 대응하는 파일 열기(import, load)가 지원되는지 확인한다.
- Declaration: `Source/NXDLio/NXDLio.h:203`
- Implementation: `Source/NXDLio/XRasterIO.cpp:92`

## IsKeyImportSupported
- Description: 특정 파일 형식의 파일 열기(import, load) 기능을 지원하는지 확인한다.
- Declaration: `Source/NXDLio/NXDLio.h:213`
- Implementation: `Source/NXDLio/XRasterIO.cpp:122`

## LoadFile
- Description: 래스터 파일을 로딩한다. 통계값 계산 여부, 영상 피라미드 생성 매개변수를 사용한다.
- Declaration: `Source/NXDLio/NXDLio.h:222`, `Source/NXDLio/NXDLio.h:230`, `Source/NXDLio/NXDLio.h:240`, `Source/NXDLio/NXDLio.h:249`, `Source/NXDLio/NXDLio.h:260`, `Source/NXDLio/NXDLio.h:271`, `Source/NXDLio/NXDLio.h:285`
- Implementation: `Source/NXDLio/XRasterIO.cpp:137`, `Source/NXDLio/XRasterIO.cpp:142`, `Source/NXDLio/XRasterIO.cpp:171`, `Source/NXDLio/XRasterIO.cpp:203`, `Source/NXDLio/XRasterIO.cpp:455`, `Source/NXDLio/XRasterIO.cpp:460`, `Source/NXDLio/XRasterIO.cpp:492`

## LoadRawFile
- Description: BIL, BIP, BSQ 형식의 래스터 데이터 파일을 로딩한다.
- Declaration: `Source/NXDLio/NXDLio.h:557`
- Implementation: `Source/NXDLio/XRasterIO.cpp:527`

## SetConfigOption
- Description: 드라이버의 설정 옵션을 변경한다.
- Declaration: `Source/NXDLio/NXDLio.h:672`
- Implementation: `Source/NXDLio/XRasterIO.cpp:1004`
