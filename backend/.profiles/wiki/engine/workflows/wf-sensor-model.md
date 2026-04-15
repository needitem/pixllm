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
required_facts:
  - symbol: XFrameSensor.SetParamsLocal
    declaration: 'bool	SetParamsLocal(XFrameSensorParams^ param);'
    source: 'Source/NXDLsm/NXDLsm.h:273'
  - symbol: XFrameSensor.SetParamsEarth
    declaration: 'bool	SetParamsEarth(XFrameSensorParams^ param);'
    source: 'Source/NXDLsm/NXDLsm.h:268'
  - symbol: XSensorModel.WorldToImageE
    declaration: 'virtual bool	WorldToImageE(NXDL::XVertex3d^ ptEuc, [OutAttribute] XVertex2d^% ptImg);'
    source: 'Source/NXDLsm/NXDLsm.h:57'
  - symbol: XSensorModel.ImageToWorldE
    declaration: 'virtual bool	ImageToWorldE(XVertex2d^ ptImg, double hEuc, [OutAttribute] NXDL::XVertex3d^% ptEuc);'
    source: 'Source/NXDLsm/NXDLsm.h:64'
  - symbol: XSensorModel.WorldToImageG
    declaration: 'virtual bool	WorldToImageG(NXDL::XVertex3d^ ptGeo,[OutAttribute] NXDL::XVertex2d^% ptImg);'
    source: 'Source/NXDLsm/NXDLsm.h:70'
  - symbol: XSensorModel.ImageToWorldG
    declaration: 'virtual bool	ImageToWorldG(NXDL::XVertex2d^ ptImg, const double hGeo, [OutAttribute] NXDL::XVertex3d^% ptGeo);'
    source: 'Source/NXDLsm/NXDLsm.h:77'
  - symbol: XSensorModel.GetMapCoordOfImageCenter
    declaration: 'virtual NXDL::XVertex3d^ GetMapCoordOfImageCenter();'
    source: 'Source/NXDLsm/NXDLsm.h:81'
verification_rules:
  - use_this_workflow_as_primary_path
  - verify_method_vs_property_form
  - verify_ref_out_and_enum_literals_when_signature_matters
  - cross_check_matching_methods_page_before_emitting_code
```
