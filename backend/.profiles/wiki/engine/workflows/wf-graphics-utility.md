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
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
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
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```

## Output Guidance
- Explanation requests: summarize the ordered call chain, prerequisites, and verified source anchors.
- Code/sample requests: prefer a focused helper, method, or minimal snippet unless the user explicitly asks for a full app shell.
- Keep the sample scoped to this workflow and do not mix neighboring subsystems unless the user explicitly asks for them.

## Common Wrong Patterns
- Do not invent helper methods or short overloads outside the verified symbol set above.
- Do not convert verified methods into properties, or properties into methods, without source proof.
- Do not guess `ref`/`out`, enum literals, or return types from naming alone.
- Do not skip prerequisites implied by the ordered call chain in this workflow.
