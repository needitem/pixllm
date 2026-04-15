---
title: Image Processing Workflow
aliases:
  - Image Processing Workflow
  - wf-image-processing
  - wf image processing
symbols:
  - NXImageLayer
  - eImageProcessingFilter
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Apply shader or filter processing to NXImageLayer.
- Core calls:
  - `NXImageLayer.EnableShaderAlgorithm`
  - `NXImageLayer.SetShaderAlgorithm`
  - `NXImageLayer.GenShaderCodeCBS`
  - `NXImageLayer.GenShaderCodeHDR`
  - `NXImageLayer.GenShaderCodeEdge`
  - `NXImageLayer.GenShaderCodeBasso`
  - `NXImageLayer.GenShaderCodeAverage`
  - `NXImageLayer.GenShaderCodeMedian`
  - `NXImageLayer.SetFilterType`
  - `NXImageLayer.SetFilterSize`
- Verified source:
  - `Source/NXImage/NXImageLayer.h:101`
  - `Source/NXImage/NXImageLayer.h:106`
  - `Source/NXImage/NXImageLayer.h:119`
  - `Source/NXImage/NXImageLayer.h:127`
  - `Source/NXImage/NXImageLayer.h:152`
  - `Source/NXImage/NXImageLayer.h:177`
  - `Source/NXImage/NXImageLayer.h:202`
  - `Source/NXImage/NXImageLayer.h:227`
  - `Source/NXImage/NXImageLayer.h:235`
  - `Source/NXImage/NXImageLayer.h:262`
- Steps:
  - shader 경로인지 filter 경로인지 먼저 정한다.
  - EnableShaderAlgorithm(true)를 켠다.
  - 질문한 GenShaderCode 또는 Filter API를 적용한다.
  - 다시 그린다.


## Required Facts
```yaml
workflow_family: image_view
output_shape: hosted_wpf_shell_by_default
required_output_files:
  - MainWindow.xaml
  - MainWindow.xaml.cs
  - App.xaml
  - App.xaml.cs
required_symbols:
  - NXImageLayer.EnableShaderAlgorithm
  - NXImageLayer.SetShaderAlgorithm
  - NXImageLayer.GenShaderCodeCBS
  - NXImageLayer.GenShaderCodeHDR
  - NXImageLayer.GenShaderCodeEdge
  - NXImageLayer.GenShaderCodeBasso
  - NXImageLayer.GenShaderCodeAverage
  - NXImageLayer.GenShaderCodeMedian
  - NXImageLayer.SetFilterType
  - NXImageLayer.SetFilterSize
required_facts:
  - symbol: NXImageLayer.EnableShaderAlgorithm
    declaration: 'bool	EnableShaderAlgorithm(bool bEnable);'
    source: 'Source/NXImage/NXImageLayer.h:101'
  - symbol: NXImageLayer.SetShaderAlgorithm
    declaration: 'bool	SetShaderAlgorithm(String^ strCode);'
    source: 'Source/NXImage/NXImageLayer.h:106'
  - symbol: NXImageLayer.GenShaderCodeCBS
    declaration: 'String^	GenShaderCodeCBS();'
    source: 'Source/NXImage/NXImageLayer.h:119'
  - symbol: NXImageLayer.GenShaderCodeHDR
    declaration: 'String^	GenShaderCodeHDR();'
    source: 'Source/NXImage/NXImageLayer.h:127'
  - symbol: NXImageLayer.GenShaderCodeEdge
    declaration: 'String^ GenShaderCodeEdge();'
    source: 'Source/NXImage/NXImageLayer.h:152'
  - symbol: NXImageLayer.GenShaderCodeBasso
    declaration: 'String^ GenShaderCodeBasso();'
    source: 'Source/NXImage/NXImageLayer.h:177'
  - symbol: NXImageLayer.GenShaderCodeAverage
    declaration: 'String^ GenShaderCodeAverage();'
    source: 'Source/NXImage/NXImageLayer.h:202'
  - symbol: NXImageLayer.GenShaderCodeMedian
    declaration: 'String^ GenShaderCodeMedian();'
    source: 'Source/NXImage/NXImageLayer.h:227'
  - symbol: NXImageLayer.SetFilterType
    declaration: 'void	SetFilterType(eImageProcessingFilter type);'
    source: 'Source/NXImage/NXImageLayer.h:262'
  - symbol: NXImageLayer.SetFilterSize
    declaration: 'void	SetFilterSize(int nSize);'
    source: 'Source/NXImage/NXImageLayer.h:235'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
