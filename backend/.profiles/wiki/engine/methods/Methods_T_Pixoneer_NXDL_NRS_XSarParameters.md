---
title: Pixoneer.NXDL.NRS.XSarParameters Methods
aliases:
  - XSarParameters Methods
  - Pixoneer.NXDL.NRS.XSarParameters
  - XSarParameters
symbols:
  - XSarParameters
  - GetAAPG
  - GetAzimuthSteering
  - GetAzimuthTime
  - GetCalSignal
  - GetElevationSteering
  - GetFDC
  - GetFDC2D
  - GetFDCRange
  - GetNoiseSignal
  - GetPRITime
  - GetRangeCompAmbiguousDopplerCentroid
  - GetRangeFirstTime
  - GetRAPG
  - GetRawAmbiguousDopplerCentroid
  - GetRawBias
  - GetRawGainImbalance
  - SetAAPG
  - SetAzimuthSteering
  - SetAzimuthTime
  - SetElevationSteering
  - SetFDC
  - SetFDC2D
  - SetFDCRange
  - SetPRITime
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nrs
---

# Overview
- Namespace: `Pixoneer.NXDL.NRS`
- Type: `XSarParameters`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XSarParameters.htm`
- Type declaration: `Source/NXDLrs/XRSFile.h:233`
- Method count: `30`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NRS.XSarParameters
type_name: XSarParameters
namespace: Pixoneer.NXDL.NRS
method_section_prefix: "## "
verification_rules:
  - treat_declaration_lines_as_symbol_existence_evidence
  - treat_implementation_lines_as_source_anchor_evidence
  - use_this_page_only_after_a_workflow_or_type_hint_narrows_scope
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page only as a verification layer after a workflow or explicit type hint identifies the target type.
- Cross-check declaration and implementation lines when overloads, properties, or call shapes matter.
- Do not synthesize end-to-end usage answers from this page alone.
## GetAAPG
- Description: AAPG(Azimuth Antenna Pattern Gains)값을 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:270`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:121`

## GetAzimuthSteering
- Description: 각 Burst의 Echo 신호에 대한 Azimuth Steering 값을 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:332`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:391`

## GetAzimuthTime
- Description: 각 Burst의 Echo 신호에 대한 시작과 종료 시점에서의 Azimuth 시간 값을 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:296`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:215`

## GetCalSignal
- Description: (Start, Echo, Stop)단계의 Cal 신호의 데이터를 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:389`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:943`

## GetElevationSteering
- Description: 각 Burst의 Echo 신호에 대한 Elevation Steering 값을 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:344`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:452`

## GetFDC
- Description: FDC(Doppler Centroid Polynomial Coefficient)값을 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:254`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:59`

## GetFDC2D
- Description: K6 영상 attribute 중 Doppler Centroid vs 2D Azimuth Range Time Polynomial Attitude Measured 값을 가져온다. 33개의 double 값을 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:286`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:170`

## GetFDCRange
- Description: K5 영상 attribute 중 Centroid vs Range Time Polynomial 값을 얻는다. 6개의 double 값을 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:278`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:146`

## GetNoiseSignal
- Description: (Start, Echo, Stop)단계의 Noise 신호의 데이터를 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:394`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:961`

## GetPRITime
- Description: 가변 PRI의 경우 각 Burst의 Echo 신호에 대한 PRI 값을 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:320`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:329`

## GetRangeCompAmbiguousDopplerCentroid
- Description: 각 Burst의 RAW Statistics Block에 대한 RangeComp Ambiguous Doppler Centroid 값을 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:374`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:772`

## GetRangeFirstTime
- Description: 각 Burst의 Echo 신호에 대한 Range 방향 수신 시작 시간 값을 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:308`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:268`

## GetRAPG
- Description: RAPG(Range Antenna Pattern Gains)값을 얻는다.
- Declaration: `Source/NXDLrs/XRSFile.h:262`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:90`

## GetRawAmbiguousDopplerCentroid
- Description: 각 Burst의 RAW Statistics Block에 대한 Raw Ambiguous Doppler Centroid 값을 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:364`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:656`

## GetRawBias
- Description: 각 Burst의 RAW Statistics Block에 대한 Raw Bias 값을 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:354`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:540`

## GetRawGainImbalance
- Description: 각 Burst의 RAW Statistics Block에 대한 Raw Gain Imbalance 값을 가져온다.
- Declaration: `Source/NXDLrs/XRSFile.h:384`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:888`

## SetAAPG
- Description: AAPG(Azimuth Antenna Pattern Gains)값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:266`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:102`

## SetAzimuthSteering
- Description: 각 Burst의 Echo 신호에 대한 Azimuth Steering 값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:326`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:354`

## SetAzimuthTime
- Description: 각 Burst의 Echo 신호에 대한 시작과 종료 시점에서의 Azimuth 시간 값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:291`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:183`

## SetElevationSteering
- Description: 각 Burst의 Echo 신호에 대한 Elevation Steering 값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:338`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:416`

## SetFDC
- Description: FDC(Doppler Centroid Polynomial Coefficient)값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:250`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:47`

## SetFDC2D
- Description: K6 영상 attribute 중 Doppler Centroid vs 2D Azimuth Range Time Polynomial Attitude Measured 값을 저장한다. 33개의 double 값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:282`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:157`

## SetFDCRange
- Description: K5 영상 attribute 중 Centroid vs Range Time Polynomial 값을 저장한다. 6개의 double 값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:274`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:133`

## SetPRITime
- Description: 가변 PRI의 경우 각 Burst의 Echo 신호에 대한 PRI 값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:314`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:293`

## SetRangeCompAmbiguousDopplerCentroid
- Description: 각 Burst의 RAW Statistics Block에 대한 RangeComp Ambiguous Doppler Centroid 값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:369`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:711`

## SetRangeFirstTime
- Description: 각 Burst의 Echo 신호에 대한 Range 방향 수신 시작 시간 값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:302`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:236`

## SetRAPG
- Description: RAPG(Range Antenna Pattern Gains)값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:258`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:70`

## SetRawAmbiguousDopplerCentroid
- Description: 각 Burst의 RAW Statistics Block에 대한 Raw Ambiguous Doppler Centroid 값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:359`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:595`

## SetRawBias
- Description: 각 Burst의 RAW Statistics Block에 대한 Raw Bias 값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:349`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:477`

## SetRawGainImbalance
- Description: 각 Burst의 RAW Statistics Block에 대한 Raw Gain Imbalance 값을 저장한다.
- Declaration: `Source/NXDLrs/XRSFile.h:379`
- Implementation: `Source/NXDLrs/XSarParameters.cpp:827`
