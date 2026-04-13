---
title: Pixoneer.NXDL.NXImage.NXImageView Methods
aliases:
  - NXImageView Methods
  - Pixoneer.NXDL.NXImage.NXImageView
  - NXImageView
symbols:
  - NXImageView
  - AddImageLayer
  - BackgroundMapInvalidate
  - CalculateScale
  - CaptureCompLayers
  - CaptureScreen
  - ClearLayer
  - GetBackgroundMapBoundRect
  - GetBackgroundMapCutType
  - GetBackgroundMapStretchCoverage
  - GetBackgroundMapStretchType
  - GetHandle
  - GetMouseControlMode
  - GetRotationAngle
  - GetScreenBound
  - GetWorldPerScreen
  - GetWorldToCenter
  - IsUnderMouse
  - LinkCameraFrom
  - RefreshScreen
  - RemoveImageLayer
  - ScreenToWorld
  - SetBackgroundMap
  - SetBackgroundMapCutType
  - SetBackgroundMapStretchCoverage
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
- Type: `NXImageView`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXImage_NXImageView.htm`
- Type declaration: `Source/NXImage/NXImageView.h:55`
- Method count: `39`

## AddImageLayer
- Description: 뷰에 레이어를 추가한다.
- Declaration: `Source/NXImage/NXImageView.h:836`
- Implementation: `Source/NXImage/NXImageView.cpp:162`

## BackgroundMapInvalidate
- Description: 배경지도를 갱신하도록 하며, 컨트롤의 내용을 다시 그리도록 한다.
- Declaration: `Source/NXImage/NXImageView.h:408`
- Implementation: `Source/NXImage/NXImageView.cpp:1026`

## CalculateScale
- Description: 현재 뷰의 축척을 계산한다.
- Declaration: `Source/NXImage/NXImageView.h:344`
- Implementation: `Source/NXImage/NXImageView.cpp:847`

## CaptureCompLayers
- Description: composite 레이어 내용을 캡쳐하여 파일(jpg, bmp, jpeg, xdm)로 저장한다.
- Declaration: `Source/NXImage/NXImageView.h:290`
- Implementation: `Source/NXImage/NXImageView.cpp:819`

## CaptureScreen
- Description: composite 레이어 내용을 캡쳐하여 파일(jpg, bmp, jpeg, xdm)로 저장한다.
- Declaration: `Source/NXImage/NXImageView.h:301`
- Implementation: `Source/NXImage/NXImageView.cpp:827`

## ClearLayer
- Description: 뷰에 있는 모든 레이어를 삭제한다.
- Declaration: `Source/NXImage/NXImageView.h:112`
- Implementation: `Source/NXImage/NXImageView.cpp:82`

## GetBackgroundMapBoundRect
- Description: 배경지도 전체 영역의 world 좌표를 가져온다.
- Declaration: `Source/NXImage/NXImageView.h:404`
- Implementation: `Source/NXImage/NXImageView.cpp:1013`

## GetBackgroundMapCutType
- Description: 히스토그램을 이용하여 배경지도의 대비 조절시 Stretching에 적용될 히스토그램의 최소 최댓값 계산하기 위해 설정된 방법을 얻는다.
- Declaration: `Source/NXImage/NXImageView.h:365`
- Implementation: `Source/NXImage/NXImageView.cpp:967`

## GetBackgroundMapStretchCoverage
- Description: 배경지도의 Histogram Stretch Coverage 방법을 얻는다.
- Declaration: `Source/NXImage/NXImageView.h:391`
- Implementation: `Source/NXImage/NXImageView.cpp:1000`

## GetBackgroundMapStretchType
- Description: 배경지도의 Histogram Stretching 방법을 얻는다.
- Declaration: `Source/NXImage/NXImageView.h:379`
- Implementation: `Source/NXImage/NXImageView.cpp:987`

## GetHandle
- Description: 뷰의 핸들을 가져온다.
- Declaration: `Source/NXImage/NXImageView.h:119`
- Implementation: `Source/NXImage/NXImageView.cpp:88`

## GetMouseControlMode
- Description: 설정되어 있는 마우스 제어 상태를 가져온다.
- Declaration: `Source/NXImage/NXImageView.h:340`
- Implementation: `Source/NXImage/NXImageView.cpp:841`

## GetRotationAngle
- Description: 화면의 회전각을 가져온다.
- Declaration: `Source/NXImage/NXImageView.h:275`
- Implementation: `Source/NXImage/NXImageView.cpp:658`

## GetScreenBound
- Description: 현재 화면의 경계 world 좌표를 가져온다.
- Declaration: `Source/NXImage/NXImageView.h:266`
- Implementation: `Source/NXImage/NXImageView.cpp:637`

## GetWorldPerScreen
- Description: 화면의 한 화소에 대응하는 해상도 크기를 가져온다.
- Declaration: `Source/NXImage/NXImageView.h:259`
- Implementation: `Source/NXImage/NXImageView.cpp:627`

## GetWorldToCenter
- Description: 화면 중심에 대한 world 좌표를 가져온다.
- Declaration: `Source/NXImage/NXImageView.h:247`
- Implementation: `Source/NXImage/NXImageView.cpp:607`

## IsUnderMouse
- Description: 마우스가 뷰 위에 있는지를 가져온다.
- Declaration: `Source/NXImage/NXImageView.h:791`
- Implementation: `not found`

## LinkCameraFrom
- Description: 현재의 카메라 뷰에 다른 카메라 뷰 상태를 복사한다.
- Declaration: `Source/NXImage/NXImageView.h:224`
- Implementation: `Source/NXImage/NXImageView.cpp:808`

## RefreshScreen
- Description: 화면을 갱신한다.
- Declaration: `Source/NXImage/NXImageView.h:228`
- Implementation: `Source/NXImage/NXImageView.cpp:686`

## RemoveImageLayer
- Description: 뷰에서 레이어를 분리한다.
- Declaration: `Source/NXImage/NXImageView.h:841`
- Implementation: `Source/NXImage/NXImageView.cpp:176`

## ScreenToWorld
- Description: 화면 좌표를 world 좌표로 변환한다.
- Declaration: `Source/NXImage/NXImageView.h:307`
- Implementation: `Source/NXImage/NXImageView.cpp:664`

## SetBackgroundMap
- Description: ImageView의 배경지도를 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:356`
- Implementation: `Source/NXImage/NXImageView.cpp:865`

## SetBackgroundMapCutType
- Description: 히스토그램을 이용하여 배경지도의 대비 조절시 Stretching에 적용될 히스토그램의 최소 최댓값 계산하기 위한 방법을 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:373`
- Implementation: `Source/NXImage/NXImageView.cpp:981`

## SetBackgroundMapStretchCoverage
- Description: 배경지도의 Histogram Stretch Coverage 방법을 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:397`
- Implementation: `Source/NXImage/NXImageView.cpp:1007`

## SetBackgroundMapStretchType
- Description: 배경지도의 Histogram Stretching 방법을 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:385`
- Implementation: `Source/NXImage/NXImageView.cpp:994`

## SetEnableChevronMenu
- Description: NXImageView의 확대/축소, 영상향상을 위한 기능 선택을 위한 컨트롤을 활성화할 것인지 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:795`
- Implementation: `Source/NXImage/NXImageView.cpp:1057`

## SetMouseControlMode
- Description: 확대축소, 회전, 이동의 마우스 제어 상태를 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:336`
- Implementation: `Source/NXImage/NXImageView.cpp:835`

## SetResolutionThresholdMax
- Description: 화면 도시를 위한 해상도 한계치 최댓값을 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:352`
- Implementation: `Source/NXImage/NXImageView.cpp:859`

## SetResolutionThresholdMin
- Description: 화면 도시를 위한 해상도 한계치 최솟값을 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:348`
- Implementation: `Source/NXImage/NXImageView.cpp:853`

## SetRotationAngle
- Description: 화면의 회전각을 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:271`
- Implementation: `Source/NXImage/NXImageView.cpp:650`

## SetWorld
- Description: 화면 도시 요소인 중심, 해상도, 회전값을 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:235`
- Implementation: `Source/NXImage/NXImageView.cpp:587`

## SetWorldPerScreen
- Description: 화면의 한 화소에 대응하는 해상도 크기를 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:253`
- Implementation: `Source/NXImage/NXImageView.cpp:618`

## SetWorldToCenter
- Description: 화면 중심에 대한 world 좌표를 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:241`
- Implementation: `Source/NXImage/NXImageView.cpp:598`

## SortControl
- Description: 레이어 컨트롤을 정렬한다. 디자인모드에서 사용가능하다.
- Declaration: `Source/NXImage/NXImageView.h:104`
- Implementation: `Source/NXImage/NXImageView.cpp:693`

## WorldToScreen
- Description: world 좌표를 화면 좌표로 변환한다.
- Declaration: `Source/NXImage/NXImageView.h:312`
- Implementation: `Source/NXImage/NXImageView.cpp:675`

## Zoom
- Description: 줌 요소를 입력으로 하여 확대축소한다. 1 : no zoom; 음수를 입력하면 축소, 양수를 입력하면 확대된다.
- Declaration: `Source/NXImage/NXImageView.h:211`
- Implementation: `Source/NXImage/NXImageView.cpp:568`

## ZoomFit
- Description: 화면에 그리드를 도시할지 여부를 확인하고 설정한다.
- Declaration: `Source/NXImage/NXImageView.h:198`
- Implementation: `Source/NXImage/NXImageView.cpp:550`

## ZoomFitRect
- Description: 화면에서 선택된 영역에 대해서 확대축소한다.
- Declaration: `Source/NXImage/NXImageView.h:219`
- Implementation: `Source/NXImage/NXImageView.cpp:578`

## ZoomOneToOne
- Description: 영상 해상도에 대해서 1:1로 화면에 도시되도록 확대축소하여 도시한다. 화면 중심에 도시된 영상 중 가장 위에 도시된 영상의 해상도에 대해서 1:1로 화면에 도시되도록 확대축소하여 도시한다. 화면 중심에 도시된 영상이 없을 경우, 도시된 전체 영상 중 가장 위에 도시된 영상의 해상도에 대해서 1:1로 화면에 도시하고 화면 중심을 그 영상의 중심으로 이동하여 도시한다.
- Declaration: `Source/NXImage/NXImageView.h:206`
- Implementation: `Source/NXImage/NXImageView.cpp:559`
