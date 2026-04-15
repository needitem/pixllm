---
title: Graphics Utility Workflow
aliases:
  - Graphics Utility Workflow
  - wf-graphics-utility
  - wf graphics utility
symbols:
  - XTexture
  - XFrameCaptureBuffer
  - XTextPrinter
  - XCursor
  - X3DModel
  - X3DModelDriverManager
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Use graphics-helper objects such as textures, capture buffers, text printers, cursors, and 3D-model loaders.
- Core calls:
  - `XTexture.Load`
  - `XTexture.Set`
  - `XTexture.Bind`
  - `XFrameCaptureBuffer.SetSize`
  - `XFrameCaptureBuffer.SaveFrame`
  - `XTextPrinter.Initialize`
  - `XTextPrinter.Print`
  - `XCursor.UpdateCursor`
  - `X3DModelDriverManager.Initialize`
  - `X3DModelDriverManager.LoadFile`
  - `X3DModelDriverManager.Convert`
- Verified source:
  - `Source/NXDLgr/XTexture.h:105`
  - `Source/NXDLgr/XTexture.h:365`
  - `Source/NXDLgr/XTexture.h:385`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:185`
  - `Source/NXDLgr/XFrameCaptureBuffer.h:255`
  - `Source/NXDLgr/XTextPrinter.h:90`
  - `Source/NXDLgr/XTextPrinter.h:104`
  - `Source/NXDLgr/XTextPrinter.h:123`
  - `Source/NXDLgr/XCursor.h:71`
  - `Source/NXDLgr/XCursor.h:156`
  - `Source/NXDLgr/X3DModel.h:106`
  - `Source/NXDLgr/X3DModel.h:121`
  - `Source/NXDLgr/X3DModel.h:137`
  - `Source/NXDLgr/X3DModel.h:177`
- Steps:
  - 보조 객체 종류를 고른다.
  - 렌더 컨텍스트를 가진 뷰/레이어에 연결한다.
  - 주 렌더 흐름의 보조 수단으로 사용한다.


## Required Facts
```yaml
workflow_family: graphics_utility
output_shape: focused_snippet_or_helper
required_symbols:
  - XTexture.Load
  - XTexture.Set
  - XTexture.Bind
  - XFrameCaptureBuffer.SetSize
  - XFrameCaptureBuffer.SaveFrame
  - XTextPrinter.Initialize
  - XTextPrinter.Print
  - XCursor.UpdateCursor
  - X3DModelDriverManager.Initialize
  - X3DModelDriverManager.LoadFile
  - X3DModelDriverManager.Convert
required_facts:
  - symbol: XTexture.Load
    declaration: 'bool Load(String^ strFileName);'
    source: 'Source/NXDLgr/XTexture.h:105'
  - symbol: XTexture.Set
    declaration: 'bool Set(cli::array<unsigned char>^ dibits, long width, long height, int nWidthBytes);'
    source: 'Source/NXDLgr/XTexture.h:365'
  - symbol: XTexture.Bind
    declaration: 'bool Bind();'
    source: 'Source/NXDLgr/XTexture.h:385'
  - symbol: XFrameCaptureBuffer.SetSize
    declaration: 'void SetSize(int nWidth, int nHeight, bool bFixed);'
    source: 'Source/NXDLgr/XFrameCaptureBuffer.h:185'
  - symbol: XFrameCaptureBuffer.SaveFrame
    declaration: 'bool SaveFrame(String^ strFilePath, String^ strFormatKey, bool bSaveGrayscale, [OutAttribute] String^% strError, XThread^ thd);'
    source: 'Source/NXDLgr/XFrameCaptureBuffer.h:255'
  - symbol: XTextPrinter.Initialize
    declaration_candidates:
      - declaration: 'bool	Initialize(Font^ font);'
        source: 'Source/NXDLgr/XTextPrinter.h:104'
      - declaration: 'bool	Initialize(Font^ font, bool awareDPI);'
        source: 'Source/NXDLgr/XTextPrinter.h:110'
  - symbol: XTextPrinter.Print
    declaration_candidates:
      - declaration: 'bool	Print(String^ str, XVertex3d^ posWorld, XVertex2d^ posOffset,'
        source: 'Source/NXDLgr/XTextPrinter.h:123'
      - declaration: 'bool	Print(String^ str, XVertex3d^ posWorld, eTextAlign align, Color color, bool bOutLine, Color clrOutLine);'
        source: 'Source/NXDLgr/XTextPrinter.h:136'
      - declaration: 'bool	Print(String^ str, XVertex3d^ posWorld, eTextAlign align, eTextAlignV alignv, Color color, bool bOutLine, Color clrOutLine);'
        source: 'Source/NXDLgr/XTextPrinter.h:149'
  - symbol: XCursor.UpdateCursor
    declaration: 'void UpdateCursor();'
    source: 'Source/NXDLgr/XCursor.h:156'
  - symbol: X3DModelDriverManager.Initialize
    declaration: 'bool		Initialize([OutAttribute] String^% strError);'
    source: 'Source/NXDLgr/X3DModel.h:121'
  - symbol: X3DModelDriverManager.LoadFile
    declaration_candidates:
      - declaration: 'X3DModel^	LoadFile(String^ strFileName, [OutAttribute]String^% strError);'
        source: 'Source/NXDLgr/X3DModel.h:127'
      - declaration: 'X3DModel^	LoadFile(String^ strFileName, bool bIgnoreMaterial, bool bUseDisplayList, bool bLoadBuild, [OutAttribute]String^% strError);'
        source: 'Source/NXDLgr/X3DModel.h:137'
  - symbol: X3DModelDriverManager.Convert
    declaration: 'bool		Convert(String^ strInputFileName, String^ strOutputFileName, NCC::XSpatialReference^% srIn, NCC::XSpatialReference^% srOut, [OutAttribute]String^% strError);'
    source: 'Source/NXDLgr/X3DModel.h:177'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
