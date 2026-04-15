---
title: Pixoneer.NXDL.NXVideo.XVideoEncoder Methods
aliases:
  - XVideoEncoder Methods
  - Pixoneer.NXDL.NXVideo.XVideoEncoder
  - XVideoEncoder
symbols:
  - XVideoEncoder
  - Close
  - EncodeAudioFrame
  - EncodeDataFrame
  - EncodeFrameSensorParameters
  - EncodeUasSensorParameters
  - EncodeVideoFrame
  - GetNativeEncoder
  - GetProgramID
  - Open
  - SetTimestampReference
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nxvideo
---

# Overview
- Namespace: `Pixoneer.NXDL.NXVideo`
- Type: `XVideoEncoder`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XVideoEncoder.htm`
- Type declaration: `Source/NXVideo/XVideoEncoder.h:242`
- Method count: `10`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XVideoEncoder
type_name: XVideoEncoder
namespace: Pixoneer.NXDL.NXVideo
method_section_prefix: "## "
verification_rules:
  - treat_declaration_lines_as_symbol_existence_evidence
  - treat_implementation_lines_as_source_anchor_evidence
  - prefer_this_page_over_examples_for_exact_call_shapes
  - do_not_invent_members_not_listed_here
```

## Runtime Usage
- Use this page to verify exact symbol existence before emitting code.
- Cross-check declaration and implementation lines when overloads or call shapes matter.
- Treat examples and workflow pages as composition guidance, but treat this page as the canonical member list.
## Close
- Description: 인코딩을 마무리하고 출력 동영상을 닫는다.
- Declaration: `Source/NXVideo/XVideoEncoder.h:284`
- Implementation: `Source/NXVideo/XVideoEncoder.cpp:427`

## EncodeAudioFrame
- Description: 오디오 프레임을 기본 동영상 오디오 스트림에 인코딩한다.
- Declaration: `Source/NXVideo/XVideoEncoder.h:343`, `Source/NXVideo/XVideoEncoder.h:347`, `Source/NXVideo/XVideoEncoder.h:359`, `Source/NXVideo/XVideoEncoder.h:370`
- Implementation: `Source/NXVideo/XVideoEncoder.cpp:580`, `Source/NXVideo/XVideoEncoder.cpp:587`, `Source/NXVideo/XVideoEncoder.cpp:597`, `Source/NXVideo/XVideoEncoder.cpp:608`

## EncodeDataFrame
- Description: 메타데이터를 기본 동영상 데이터 스트림에 인코딩한다.
- Declaration: `Source/NXVideo/XVideoEncoder.h:376`, `Source/NXVideo/XVideoEncoder.h:388`, `Source/NXVideo/XVideoEncoder.h:395`, `Source/NXVideo/XVideoEncoder.h:407`, `Source/NXVideo/XVideoEncoder.h:582`, `Source/NXVideo/XVideoEncoder.h:595`, `Source/NXVideo/XVideoEncoder.h:603`, `Source/NXVideo/XVideoEncoder.h:616`, `Source/NXVideo/XVideoEncoder.h:724`, `Source/NXVideo/XVideoEncoder.h:738`, `Source/NXVideo/XVideoEncoder.h:747`, `Source/NXVideo/XVideoEncoder.h:761`
- Implementation: `Source/NXVideo/XVideoEncoder.cpp:621`, `Source/NXVideo/XVideoEncoder.cpp:626`, `Source/NXVideo/XVideoEncoder.cpp:630`, `Source/NXVideo/XVideoEncoder.cpp:640`, `Source/NXVideo/XVideoEncoder.cpp:645`, `Source/NXVideo/XVideoEncoder.cpp:650`, `Source/NXVideo/XVideoEncoder.cpp:663`, `Source/NXVideo/XVideoEncoder.cpp:668`, `Source/NXVideo/XVideoEncoder.cpp:672`, `Source/NXVideo/XVideoEncoder.cpp:680`, `Source/NXVideo/XVideoEncoder.cpp:685`, `Source/NXVideo/XVideoEncoder.cpp:690`

## EncodeFrameSensorParameters
- Description: XFrameSensor로 표현된 센서 데이터를 MISB ST 0601에 따라 기본 동영상 데이터 스트림에 인코딩한다. 지구 모드 센서 데이터가 입력되어야 하며, 플랫폼 자세가 주어질 경우 플랫폼 자세와 센서 자세를 분리하여 인코딩한다. PTS와 타임스탬프는 인코딩 파라미터에 따라 순차적으로 부여된다.
- Declaration: `Source/NXVideo/XVideoEncoder.h:466`, `Source/NXVideo/XVideoEncoder.h:484`, `Source/NXVideo/XVideoEncoder.h:502`, `Source/NXVideo/XVideoEncoder.h:678`, `Source/NXVideo/XVideoEncoder.h:697`, `Source/NXVideo/XVideoEncoder.h:716`, `Source/NXVideo/XVideoEncoder.h:827`, `Source/NXVideo/XVideoEncoder.h:847`, `Source/NXVideo/XVideoEncoder.h:867`
- Implementation: `Source/NXVideo/XVideoEncoder.cpp:777`, `Source/NXVideo/XVideoEncoder.cpp:782`, `Source/NXVideo/XVideoEncoder.cpp:787`, `Source/NXVideo/XVideoEncoder.cpp:792`, `Source/NXVideo/XVideoEncoder.cpp:797`, `Source/NXVideo/XVideoEncoder.cpp:802`, `Source/NXVideo/XVideoEncoder.cpp:807`, `Source/NXVideo/XVideoEncoder.cpp:813`, `Source/NXVideo/XVideoEncoder.cpp:874`

## EncodeUasSensorParameters
- Description: MISB ST 0601에 따라 센서/플랫폼 자세, 위치, 화각을 기본 동영상 데이터 스트림에 인코딩한다. PTS와 타임스탬프는 인코딩 파라미터에 따라 순차적으로 부여된다.
- Declaration: `Source/NXVideo/XVideoEncoder.h:418`, `Source/NXVideo/XVideoEncoder.h:436`, `Source/NXVideo/XVideoEncoder.h:454`, `Source/NXVideo/XVideoEncoder.h:627`, `Source/NXVideo/XVideoEncoder.h:646`, `Source/NXVideo/XVideoEncoder.h:665`, `Source/NXVideo/XVideoEncoder.h:773`, `Source/NXVideo/XVideoEncoder.h:793`, `Source/NXVideo/XVideoEncoder.h:813`
- Implementation: `Source/NXVideo/XVideoEncoder.cpp:701`, `Source/NXVideo/XVideoEncoder.cpp:707`, `Source/NXVideo/XVideoEncoder.cpp:713`, `Source/NXVideo/XVideoEncoder.cpp:719`, `Source/NXVideo/XVideoEncoder.cpp:727`, `Source/NXVideo/XVideoEncoder.cpp:735`, `Source/NXVideo/XVideoEncoder.cpp:741`, `Source/NXVideo/XVideoEncoder.cpp:757`, `Source/NXVideo/XVideoEncoder.cpp:767`

## EncodeVideoFrame
- Description: 영상 프레임을 인코딩 파라미터에 따라 기본 동영상 비디오 스트림에 인코딩한다. 인코딩 파라미터 XEncodeParam.CopyPts 값에 따라 입력 프레임의 PTS를 출력에 활용한다.
- Declaration: `Source/NXVideo/XVideoEncoder.h:293`, `Source/NXVideo/XVideoEncoder.h:304`, `Source/NXVideo/XVideoEncoder.h:310`, `Source/NXVideo/XVideoEncoder.h:323`, `Source/NXVideo/XVideoEncoder.h:337`, `Source/NXVideo/XVideoEncoder.h:527`, `Source/NXVideo/XVideoEncoder.h:539`, `Source/NXVideo/XVideoEncoder.h:546`, `Source/NXVideo/XVideoEncoder.h:560`, `Source/NXVideo/XVideoEncoder.h:575`
- Implementation: `Source/NXVideo/XVideoEncoder.cpp:451`, `Source/NXVideo/XVideoEncoder.cpp:458`, `Source/NXVideo/XVideoEncoder.cpp:462`, `Source/NXVideo/XVideoEncoder.cpp:480`, `Source/NXVideo/XVideoEncoder.cpp:485`, `Source/NXVideo/XVideoEncoder.cpp:504`, `Source/NXVideo/XVideoEncoder.cpp:509`, `Source/NXVideo/XVideoEncoder.cpp:528`, `Source/NXVideo/XVideoEncoder.cpp:533`, `Source/NXVideo/XVideoEncoder.cpp:554`, `Source/NXVideo/XVideoEncoder.cpp:559`

## GetNativeEncoder
- Description: XDL 내부 비관리 객체 XVideoEndcoder 포인터를 얻는다.
- Declaration: `Source/NXVideo/XVideoEncoder.h:262`
- Implementation: `not found`

## GetProgramID
- Description: 동영상 프로그램 식별자를 얻는다. 단일 프로그램 동영상인 경우 기본 프로그램 식별자는 1이다.
- Declaration: `Source/NXVideo/XVideoEncoder.h:287`
- Implementation: `Source/NXVideo/XVideoEncoder.cpp:432`

## Open
- Description: 비어 있는 다중 프로그램 동영상 출력을 생성한다.
- Declaration: `Source/NXVideo/XVideoEncoder.h:272`, `Source/NXVideo/XVideoEncoder.h:277`, `Source/NXVideo/XVideoEncoder.h:281`
- Implementation: `Source/NXVideo/XVideoEncoder.cpp:368`, `Source/NXVideo/XVideoEncoder.cpp:374`, `Source/NXVideo/XVideoEncoder.cpp:419`

## SetTimestampReference
- Description: 기본 동영상 프로그램의 메타데이터 기준 시각을 설정한다.
- Declaration: `Source/NXVideo/XVideoEncoder.h:512`, `Source/NXVideo/XVideoEncoder.h:520`, `Source/NXVideo/XVideoEncoder.h:877`, `Source/NXVideo/XVideoEncoder.h:886`
- Implementation: `Source/NXVideo/XVideoEncoder.cpp:883`, `Source/NXVideo/XVideoEncoder.cpp:888`, `Source/NXVideo/XVideoEncoder.cpp:893`, `Source/NXVideo/XVideoEncoder.cpp:898`
