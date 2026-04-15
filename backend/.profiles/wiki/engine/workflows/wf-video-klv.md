---
title: Video KLV Workflow
aliases:
  - Video KLV Workflow
  - wf-video-klv
  - wf video klv
symbols:
  - NXMpegTSAnalysis
  - XKLVManager
  - XFrameMetad
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Extract KLV metadata from MPEG-TS and decode it through engine helpers.
- Core calls:
  - `NXMpegTSAnalysis.GetKLVMetaData`
  - `XKLVManager.ParseKLVData`
  - `XKLVManager.GetKLVCount`
  - `XKLVManager.GetKey`
  - `XKLVManager.GetValue`
  - `XFrameMetad.GetData`
  - `XFrameMetad.SetData`
  - `XFrameMetad.Decode`
- Verified source:
  - `Source/NXVideo/NXMpegTSAnalysis.h:41`
  - `Source/NXVideo/XKLVManager.h:31`
  - `Source/NXVideo/XKLVManager.h:35`
  - `Source/NXVideo/XKLVManager.h:39`
  - `Source/NXVideo/XKLVManager.h:44`
  - `Source/NXVideo/XKLVManager.h:49`
  - `Source/NXVideo/XFrameMetad.h:120`
  - `Source/NXVideo/XFrameMetad.h:126`
  - `Source/NXVideo/XFrameMetad.h:143`
- Steps:
  - TS 패킷에서 KLV를 추출한다.
  - 원시 키/값은 XKLVManager로 파싱한다.
  - typed metadata는 XFrameMetad로 decode한다.


## Required Facts
```yaml
workflow_family: video_view
output_shape: hosted_wpf_shell_by_default
required_output_files:
  - MainWindow.xaml
  - MainWindow.xaml.cs
  - App.xaml
  - App.xaml.cs
required_symbols:
  - NXMpegTSAnalysis.GetKLVMetaData
  - XKLVManager.ParseKLVData
  - XKLVManager.GetKLVCount
  - XKLVManager.GetKey
  - XKLVManager.GetValue
  - XFrameMetad.GetData
  - XFrameMetad.SetData
  - XFrameMetad.Decode
required_facts:
  - symbol: NXMpegTSAnalysis.GetKLVMetaData
    declaration: 'bool GetKLVMetaData(cli::array<unsigned char>^ packet_data, int length, [OutAttribute] cli::array<unsigned char>^% meta_data);'
    source: 'Source/NXVideo/NXMpegTSAnalysis.h:41'
  - symbol: XKLVManager.ParseKLVData
    declaration: 'void			ParseKLVData(cli::array<byte>^ data);'
    source: 'Source/NXVideo/XKLVManager.h:35'
  - symbol: XKLVManager.GetKLVCount
    declaration: 'int				GetKLVCount();'
    source: 'Source/NXVideo/XKLVManager.h:39'
  - symbol: XKLVManager.GetKey
    declaration: 'cli::array<byte>^	GetKey(int nIndex);'
    source: 'Source/NXVideo/XKLVManager.h:44'
  - symbol: XKLVManager.GetValue
    declaration: 'cli::array<byte>^	GetValue(int nIndex);'
    source: 'Source/NXVideo/XKLVManager.h:49'
  - symbol: XFrameMetad.GetData
    declaration: 'cli::array<byte>^ GetData();'
    source: 'Source/NXVideo/XFrameMetad.h:120'
  - symbol: XFrameMetad.SetData
    declaration: 'bool SetData(cli::array<byte>^ data, eMetadataType type);'
    source: 'Source/NXVideo/XFrameMetad.h:126'
  - symbol: XFrameMetad.Decode
    declaration_candidates:
      - declaration: 'bool Decode();'
        source: 'Source/NXVideo/XFrameMetad.h:138'
      - declaration: 'bool Decode(XUASLocalSetDecoder^ decoder);'
        source: 'Source/NXVideo/XFrameMetad.h:143'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
