---
title: Image Background Map Workflow
aliases:
  - Image Background Map Workflow
  - wf-image-background-map
  - wf image background map
symbols:
  - NXImageView
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Configure background-map settings on NXImageView.
- Core calls:
  - `NXImageView.SetBackgroundMap`
  - `NXImageView.BackgroundMapVisible`
  - `NXImageView.BackgroundMapAlpha`
  - `NXImageView.BackgroundMapContrast`
  - `NXImageView.BackgroundMapBrightness`
  - `NXImageView.BackgroundMapSaturation`
  - `NXImageView.BackgroundMapInterpolPixel`
- Verified source:
  - `Source/NXImage/NXImageView.h:168`
  - `Source/NXImage/NXImageView.h:171`
  - `Source/NXImage/NXImageView.h:174`
  - `Source/NXImage/NXImageView.h:177`
  - `Source/NXImage/NXImageView.h:180`
  - `Source/NXImage/NXImageView.h:183`
  - `Source/NXImage/NXImageView.h:356`
- Steps:
  - SetBackgroundMap으로 배경지도를 연결한다.
  - BackgroundMap 속성으로 표시/화질을 조절한다.
  - 화면 갱신을 수행한다.


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
  - NXImageView.SetBackgroundMap
  - NXImageView.BackgroundMapVisible
  - NXImageView.BackgroundMapAlpha
  - NXImageView.BackgroundMapContrast
  - NXImageView.BackgroundMapBrightness
  - NXImageView.BackgroundMapSaturation
  - NXImageView.BackgroundMapInterpolPixel
required_facts:
  - symbol: NXImageView.SetBackgroundMap
    declaration: 'bool		SetBackgroundMap(String^ strConfig);'
    source: 'Source/NXImage/NXImageView.h:356'
  - symbol: NXImageView.BackgroundMapVisible
    declaration: 'property bool BackgroundMapVisible	  { bool get(); void set(bool val); }'
    source: 'Source/NXImage/NXImageView.h:168'
  - symbol: NXImageView.BackgroundMapAlpha
    declaration: 'property float BackgroundMapAlpha		{ float get();	void set(float val); }'
    source: 'Source/NXImage/NXImageView.h:171'
  - symbol: NXImageView.BackgroundMapContrast
    declaration: 'property float BackgroundMapContrast		{ float get();	void set(float val); }'
    source: 'Source/NXImage/NXImageView.h:174'
  - symbol: NXImageView.BackgroundMapBrightness
    declaration: 'property float BackgroundMapBrightness	{ float get();	void set(float val); }'
    source: 'Source/NXImage/NXImageView.h:177'
  - symbol: NXImageView.BackgroundMapSaturation
    declaration: 'property float BackgroundMapSaturation	{ float get();	void set(float val); }'
    source: 'Source/NXImage/NXImageView.h:180'
  - symbol: NXImageView.BackgroundMapInterpolPixel
    declaration: 'property bool BackgroundMapInterpolPixel { bool get();	void set(bool value); }'
    source: 'Source/NXImage/NXImageView.h:183'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
