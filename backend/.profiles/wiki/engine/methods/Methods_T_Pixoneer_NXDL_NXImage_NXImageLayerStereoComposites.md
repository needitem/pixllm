---
title: Pixoneer.NXDL.NXImage.NXImageLayerStereoComposites Methods
aliases:
  - NXImageLayerStereoComposites Methods
  - Pixoneer.NXDL.NXImage.NXImageLayerStereoComposites
  - NXImageLayerStereoComposites
symbols:
  - NXImageLayerStereoComposites
  - ConvRightImagePosition
  - FindMatchPoint
  - GetMatchKernelSize
  - GetSearchOffset
  - GetXDMCompManagerL
  - GetXDMCompManagerR
  - Invalidate
  - Lock
  - SetMatchKernelSize
  - SetSearchOffset
  - SetYOffSetConst
  - SyncStereoViewPixelOffset
  - UnLock
  - ZoomFit
  - ZoomOneToOne
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
  - nximage
---

# Overview
- Namespace: `Pixoneer.NXDL.NXImage`
- Type: `NXImageLayerStereoComposites`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXImage_NXImageLayerStereoComposites.htm`
- Type declaration: `Source/NXImage/NXImageLayerStereoComposites.h:128`
- Method count: `15`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXImage.NXImageLayerStereoComposites
type_name: NXImageLayerStereoComposites
namespace: Pixoneer.NXDL.NXImage
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
## ConvRightImagePosition
- Description: 왼쪽 커서의 영상 화소 위치를 오른쪽 커서의 화소 위치로 변환한다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:211`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:96`

## FindMatchPoint
- Description: 오른쪽 영상 화소 위치를 입력 왼쪽 영상 화소 위치와 맞는 위치를 찾는다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:197`, `Source/NXImage/NXImageLayerStereoComposites.h:204`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:119`, `Source/NXImage/NXImageLayerStereoComposites.cpp:126`

## GetMatchKernelSize
- Description: 영상 매칭을 위한 커널 크기를 가져온다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:177`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:140`

## GetSearchOffset
- Description: 영상 매칭을 위한 검색 오프셋을 가져온다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:191`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:154`

## GetXDMCompManagerL
- Description: 왼쪽 composite 관리자를 가져온다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:146`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:86`

## GetXDMCompManagerR
- Description: 오른쪽 composite 관리자를 가져온다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:150`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:91`

## Invalidate
- Description: 전체 화면을 갱신하도록 하며, 컨트롤의 내용을 다시 그리도록 한다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:237`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:67`

## Lock
- Description: XDMCompManager 객체를 다른 쓰레드에서 변경하지 못하도록 제한한다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:226`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:74`

## SetMatchKernelSize
- Description: 영상 매칭을 위한 커널 크기를 설정한다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:172`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:134`

## SetSearchOffset
- Description: 영상 매칭을 위한 검색 오프셋을 설정한다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:184`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:148`

## SetYOffSetConst
- Description: Y 방향으로의 커서 오프셋을 설정한다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:241`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:213`

## SyncStereoViewPixelOffset
- Description: ImageView 인수를 이용하여 화소 오프셋 매개변수(스테레어 매개변수)를 동기화한다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:214`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:207`

## UnLock
- Description: XDMCompManager 객체의 제한 설정을 해제한다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:230`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:80`

## ZoomFit
- Description: 화면에 전체 영상이 보이도록 확대축소한다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:218`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:55`

## ZoomOneToOne
- Description: 영상의 해상도에 대해 1:1로 도시하도록 확대축소한다.
- Declaration: `Source/NXImage/NXImageLayerStereoComposites.h:222`
- Implementation: `Source/NXImage/NXImageLayerStereoComposites.cpp:61`
