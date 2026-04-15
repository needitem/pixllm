---
title: Planet Dataset Workflow
aliases:
  - Planet Dataset Workflow
  - wf-planet-dataset
  - wf planet dataset
symbols:
  - NXPlanetView
  - XPBTDataGroup
  - XPBTDataSource
  - NXPlanetEngine
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Register PBI groups and switch the default dataset set.
- Core calls:
  - `NXPlanetView.SetPBIDefaultDataSet`
  - `XPBTDataGroup.Sources.Add`
  - `NXPlanetEngine.AddPBIGroup`
  - `NXPlanetEngine.RemovePBIGroup`
- Verified source:
  - `Source/NXPlanet/NXPlanetView.h:151`
  - `Source/NXPlanet/NXPlanetView.h:168`
  - `Source/NXPlanet/NXPlanetView.h:171`
  - `Source/NXPlanet/NXPlanetView.h:193`
  - `Source/NXPlanet/NXPlanetView.h:210`
  - `Source/NXPlanet/NXPlanetView.h:212`
  - `Source/NXPlanet/NXPlanetView.h:694`
- Steps:
  - data group와 source를 만든다.
  - 엔진에 그룹을 등록/교체한다.
  - SetPBIDefaultDataSet으로 활성 조합을 고른다.


## Required Facts
```yaml
workflow_family: map_view
output_shape: hosted_wpf_shell_by_default
required_output_files:
  - MainWindow.xaml
  - MainWindow.xaml.cs
  - App.xaml
  - App.xaml.cs
required_symbols:
  - NXPlanetView.SetPBIDefaultDataSet
  - XPBTDataGroup.Sources.Add
  - NXPlanetEngine.AddPBIGroup
  - NXPlanetEngine.RemovePBIGroup
required_facts:
  - symbol: NXPlanetView.SetPBIDefaultDataSet
    declaration: 'void SetPBIDefaultDataSet(String^ strSource);'
    source: 'Source/NXPlanet/NXPlanetView.h:694'
  - symbol: XPBTDataGroup.Sources.Add
    declaration_candidates:
      - declaration: '///			rpfGroup.Sources.Add(src);'
        source: 'Source/NXPlanet/NXPlanetView.h:168'
      - declaration: '///			rpfGroup.Sources.Add(src);'
        source: 'Source/NXPlanet/NXPlanetView.h:210'
  - symbol: NXPlanetEngine.AddPBIGroup
    declaration: 'static bool		AddPBIGroup(XPBTDataGroup^% Group);'
    source: 'Source/NXPlanet/NXPlanetEngine.h:87'
  - symbol: NXPlanetEngine.RemovePBIGroup
    declaration: 'static bool		RemovePBIGroup(int nGroupID);'
    source: 'Source/NXPlanet/NXPlanetEngine.h:92'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
