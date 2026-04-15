---
title: Image Hosting Workflow
aliases:
  - Image Hosting Workflow
  - wf-image-hosting
  - wf image hosting
symbols:
  - NXImageView
  - NXImageLayer
  - NXImageLayerComposites
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Host NXImageView and attach image layers.
- Core calls:
  - `NXImageView.AddImageLayer`
  - `NXImageView.RemoveImageLayer`
  - `NXImageView.ClearLayer`
- Verified source:
  - `Source/NXImage/NXImageView.h:112`
  - `Source/NXImage/NXImageView.h:822`
  - `Source/NXImage/NXImageView.h:836`
  - `Source/NXImage/NXImageView.h:841`
- Steps:
  - NXImageView를 호스트에 올린다.
  - NXImageLayer 파생 레이어를 만든다.
  - AddImageLayer(ref layer)로 연결한다.
  - 필요 시 RemoveImageLayer/ClearLayer로 정리한다.


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
  - NXImageView.AddImageLayer
  - NXImageView.RemoveImageLayer
  - NXImageView.ClearLayer
required_facts:
  - symbol: NXImageView.AddImageLayer
    declaration: 'bool		AddImageLayer(NXImageLayer^% layer);'
    source: 'Source/NXImage/NXImageView.h:836'
  - symbol: NXImageView.RemoveImageLayer
    declaration: 'bool		RemoveImageLayer(NXImageLayer^ layer);'
    source: 'Source/NXImage/NXImageView.h:841'
  - symbol: NXImageView.ClearLayer
    declaration: 'void ClearLayer();'
    source: 'Source/NXImage/NXImageView.h:112'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
