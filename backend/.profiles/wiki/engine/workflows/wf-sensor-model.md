---
title: Sensor Model Workflow
aliases:
  - Sensor Model Workflow
  - wf-sensor-model
  - wf sensor model
symbols:
  - XFrameSensorParams
  - XFrameSensor
  - XSensorModel
  - XRpc
  - XSarSensor
tags:
  - engine
  - workflow
  - qa
---

# Overview
- Goal: Configure sensor models and project between image and world spaces.
- Role: normalized workflow file used by the 360-question answer index.
- Existing curated workflow/example pages should be kept and referenced, not replaced blindly.
- Core calls:
  - `XFrameSensor.SetParamsLocal`
  - `XFrameSensor.SetParamsEarth`
  - `XSensorModel.WorldToImageE`
  - `XSensorModel.ImageToWorldE`
  - `XSensorModel.WorldToImageG`
  - `XSensorModel.ImageToWorldG`
  - `XSensorModel.GetMapCoordOfImageCenter`
- Verified source:
  - `Source/NXDLsm/NXDLsm.h:57`
  - `Source/NXDLsm/NXDLsm.h:64`
  - `Source/NXDLsm/NXDLsm.h:70`
  - `Source/NXDLsm/NXDLsm.h:77`
  - `Source/NXDLsm/NXDLsm.h:81`
  - `Source/NXDLsm/NXDLsm.h:207`
  - `Source/NXDLsm/NXDLsm.h:241`
  - `Source/NXDLsm/NXDLsm.h:268`
  - `Source/NXDLsm/NXDLsm.h:273`
- Steps:
  - sensor parameter를 채운다.
  - local 또는 earth 경로를 택해 모델을 세팅한다.
  - 이후 image/world 변환 메서드를 반복 호출한다.

## Required Facts
```yaml
workflow_family: sensor_model
output_shape: focused_snippet_or_helper
required_symbols:
  - XFrameSensor.SetParamsLocal
  - XFrameSensor.SetParamsEarth
  - XSensorModel.WorldToImageE
  - XSensorModel.ImageToWorldE
  - XSensorModel.WorldToImageG
  - XSensorModel.ImageToWorldG
  - XSensorModel.GetMapCoordOfImageCenter
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
