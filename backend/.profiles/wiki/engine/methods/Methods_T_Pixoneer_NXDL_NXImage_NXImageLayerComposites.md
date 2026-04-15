---
title: Pixoneer.NXDL.NXImage.NXImageLayerComposites Methods
aliases:
  - NXImageLayerComposites Methods
  - Pixoneer.NXDL.NXImage.NXImageLayerComposites
  - NXImageLayerComposites
symbols:
  - NXImageLayerComposites
  - ClearCache
  - ClearTexture
  - EnableCache
  - EnableThread
  - GetXDMCompManager
  - HitTest
  - Invalidate
  - InvalidateCache
  - Lock
  - ReadPixelValues
  - SetEnableUpdateAtEnd
  - UnLock
  - ZoomFit
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
- Type: `NXImageLayerComposites`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXImage_NXImageLayerComposites.htm`
- Type declaration: `Source/NXImage/NXImageLayerComposites.h:123`
- Method count: `13`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXImage.NXImageLayerComposites
type_name: NXImageLayerComposites
namespace: Pixoneer.NXDL.NXImage
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
## ClearCache
- Description: 캐싱을 삭제한다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:179`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:99`

## ClearTexture
- Description: 도시를 위한 텍스처를 삭제한다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:182`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:105`

## EnableCache
- Description: 캐싱을 활성화한다. 활성화하면 panning 및 zoom in/out 시 변경된 도시 영역의 빈 공간에 영상이 로딩되기 전까지 캐싱 영상으로 임시 도시한다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:164`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:81`

## EnableThread
- Description: 렌더링 쓰레드를 활성화한다. 렌더링 쓰레드가 활성화되면 NXImageLayerComposites에서 도시되는 텍스처 생성이 Render 함수와 별개로 실행된다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:168`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:87`

## GetXDMCompManager
- Description: XDMCompManager 객체를 가져온다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:149`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:66`

## HitTest
- Description: 화면에 도시된 XDMComposite 중에서 특정 위치에 Hitting 되는 가장 상위의 XDMComposite 를 가져온다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:313`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:187`

## Invalidate
- Description: 전체 화면을 갱신하도록 하며, 컨트롤의 내용을 다시 그리도록 한다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:146`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:61`

## InvalidateCache
- Description: 캐싱을 갱신한다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:185`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:111`

## Lock
- Description: XDMCompManager 객체를 다른 쓰레드에서 변경하지 못하도록 제한한다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:153`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:71`

## ReadPixelValues
- Description: 화면에 도시된 데이터에서 화면 좌표값 기준 픽셀 화소값을 읽어 반환한다. 화소값이 없는 경우 XDataRange.MAX_REAL64 값이 반환된다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:196`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:171`

## SetEnableUpdateAtEnd
- Description: Mouse-wheel을 이용한 Smooth Zooming 또는 마우스를 이용한 panning이 실행될 때 화면 텍스처의 갱신 시점을 조정한다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:176`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:93`

## UnLock
- Description: XDMCompManager 객체의 제한 설정을 해제한다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:157`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:76`

## ZoomFit
- Description: 화면에 전체 영상이 도시되도록 확대축소하는 함수이다.
- Declaration: `Source/NXImage/NXImageLayerComposites.h:142`
- Implementation: `Source/NXImage/NXImageLayerComposites.cpp:56`
