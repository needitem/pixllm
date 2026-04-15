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
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
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
output_shape: view_shell_or_hosted_control
required_symbols:
  - NXPlanetView.SetPBIDefaultDataSet
  - XPBTDataGroup.Sources.Add
  - NXPlanetEngine.AddPBIGroup
  - NXPlanetEngine.RemovePBIGroup
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```

## Output Guidance
- Explanation requests: summarize the view initialization order, layer wiring, camera/state setup, and refresh path.
- Code/sample requests: return the host/view shell plus the ordered initialization sequence for layers, SR, and interaction state.
- If the user asks for WPF, include the XAML shell and code-behind instead of returning only a single `.cs` file.

## Common Wrong Patterns
- Do not invent helper methods or short overloads outside the verified symbol set above.
- Do not convert verified methods into properties, or properties into methods, without source proof.
- Do not guess `ref`/`out`, enum literals, or return types from naming alone.
- Do not skip prerequisites implied by the ordered call chain in this workflow.
- Do not skip the camera/state or layer setup steps when the question is about a runnable map/planet/uspace workflow.

- See also:
  - [xdl-planetview-wpf-examples.md](xdl-planetview-wpf-examples.md)
