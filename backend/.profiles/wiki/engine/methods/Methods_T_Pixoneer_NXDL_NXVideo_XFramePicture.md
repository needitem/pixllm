---
title: Pixoneer.NXDL.NXVideo.XFramePicture Methods
aliases:
  - XFramePicture Methods
  - Pixoneer.NXDL.NXVideo.XFramePicture
  - XFramePicture
symbols:
  - XFramePicture
  - ConvertToRGB
  - ConvertToYUV420P
  - FrameQueueSize
  - FrontFrameInQueue
  - GetData
  - GetDataPtr
  - GetDataPtrRGB
  - GetDataPtrU
  - GetDataPtrV
  - GetDataPtrY
  - GetDataRGB
  - GetDataU
  - GetDataV
  - GetDataY
  - GetFrame
  - GetHomography
  - GetInverseHomography
  - GetInverseMotion
  - GetMotion
  - GetNativeFrame
  - GetPacketData
  - GetPixelRGB
  - GetPixelValue
  - HasYPlane
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
- Type: `XFramePicture`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XFramePicture.htm`
- Type declaration: `Source/NXVideo/XFramePicture.h:59`
- Method count: `46`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.XFramePicture
type_name: XFramePicture
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
## ConvertToRGB
- Description: 프레임 데이터를 RGB 형식으로 바꾼다.
- Declaration: `Source/NXVideo/XFramePicture.h:248`, `Source/NXVideo/XFramePicture.h:253`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1205`, `Source/NXVideo/XFramePicture.cpp:1220`

## ConvertToYUV420P
- Description: 프레임 데이터를 YUV420P 형식으로 바꾼다.
- Declaration: `Source/NXVideo/XFramePicture.h:245`, `Source/NXVideo/XFramePicture.h:257`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1185`, `Source/NXVideo/XFramePicture.cpp:1255`

## FrameQueueSize
- Description: 비관리 프레임 큐의 길이를 구한다.
- Declaration: `Source/NXVideo/XFramePicture.h:431`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1714`

## FrontFrameInQueue
- Description: 비관리 프레임 큐의 맨 앞에 있는 프레임을 얻는다. 프레임 확인을 위한 것으로 큐에서 프레임을 꺼내지 않는다.
- Declaration: `Source/NXVideo/XFramePicture.h:415`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1668`

## GetData
- Description: 주어진 데이터 판의 데이터를 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:162`
- Implementation: `Source/NXVideo/XFramePicture.cpp:179`

## GetDataPtr
- Description: 주어진 데이터 판의 데이터 포인터를 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:148`, `Source/NXVideo/XFramePicture.h:155`
- Implementation: `Source/NXVideo/XFramePicture.cpp:147`, `Source/NXVideo/XFramePicture.cpp:160`

## GetDataPtrRGB
- Description: RGB24 형식일 때 RGB data pointer를 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:166`
- Implementation: `Source/NXVideo/XFramePicture.cpp:174`

## GetDataPtrU
- Description: Planar YUV 형식일 때 YUV의 데이터 중 U data pointer를 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:138`
- Implementation: `Source/NXVideo/XFramePicture.cpp:137`

## GetDataPtrV
- Description: Planar YUV 형식일 때 YUV의 데이터 중 V data pointer를 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:141`
- Implementation: `Source/NXVideo/XFramePicture.cpp:142`

## GetDataPtrY
- Description: Planar YUV 형식 또는 NV12와 같이 Y 판이 분리된 복합 형식일 때 YUV의 데이터 중 Y data pointer를 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:135`
- Implementation: `Source/NXVideo/XFramePicture.cpp:129`

## GetDataRGB
- Description: RGB24 형식일 때 RGB data array를 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:170`
- Implementation: `Source/NXVideo/XFramePicture.cpp:301`

## GetDataU
- Description: U data를 배열로 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:188`
- Implementation: `Source/NXVideo/XFramePicture.cpp:251`

## GetDataV
- Description: V data를 배열로 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:182`
- Implementation: `Source/NXVideo/XFramePicture.cpp:276`

## GetDataY
- Description: Y data를 배열로 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:176`
- Implementation: `Source/NXVideo/XFramePicture.cpp:226`

## GetFrame
- Description: 비관리 객체인 XFramePicture를 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:191`
- Implementation: `not found`

## GetHomography
- Description: 프레임의 호모그래피 변환 행렬(3x3)을 얻는다. 행-우선 방식으로 길이 9인 배열이다.
- Declaration: `Source/NXVideo/XFramePicture.h:393`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1560`

## GetInverseHomography
- Description: 프레임의 호모그래피 역변환 행렬(3x3)을 얻는다. 행-우선 방식으로 길이 9인 배열이다.
- Declaration: `Source/NXVideo/XFramePicture.h:395`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1577`

## GetInverseMotion
- Description: 직전 프레임 대비 움직임 역변환 행렬(3x3)을 얻는다. 행-우선 방식으로 길이 9인 배열이다.
- Declaration: `Source/NXVideo/XFramePicture.h:404`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1631`

## GetMotion
- Description: 직전 프레임 대비 움직임 변환 행렬(3x3)을 얻는다. 행-우선 방식으로 길이 9인 배열이다.
- Declaration: `Source/NXVideo/XFramePicture.h:402`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1614`

## GetNativeFrame
- Description: 비관리 프레임 객체를 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:390`
- Implementation: `not found`

## GetPacketData
- Description: 원본 패킷(JPEG) 데이터가 있을 때 복사된 바이트 배열을 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:231`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1140`

## GetPixelRGB
- Description: 특정 화소의 색상값을 RGB 형식으로 얻는다. 화소 형식이 RGB가 아닌 경우 RGB 대응값으로 변환한다.
- Declaration: `Source/NXVideo/XFramePicture.h:373`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1720`

## GetPixelValue
- Description: 특정 화소의 색상값을 원본 형식으로 얻는다. RGBA 계열을 포함하여 최대 네 개이며, 순서는 원본 화소 형식에 따라 정해진다. YUV 계열인 경우 Y,U,V 순서이나 NV21 형식은 Y,V,U 순서이다.
- Declaration: `Source/NXVideo/XFramePicture.h:386`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1732`

## HasYPlane
- Description: YUV 형식에서 독립된 Y 데이터 판을 가지는 형식인지 확인한다. Plannar YUV 형식과 NV12와 같은 복합 형식이 해당된다.
- Declaration: `Source/NXVideo/XFramePicture.h:126`
- Implementation: `Source/NXVideo/XFramePicture.cpp:112`

## IsGray
- Description: 회색조 형식인지 확인한다.
- Declaration: `Source/NXVideo/XFramePicture.h:132`
- Implementation: `Source/NXVideo/XFramePicture.cpp:123`

## IsPlanarYUV
- Description: Planar YUV 형식인지 확인한다.
- Declaration: `Source/NXVideo/XFramePicture.h:120`
- Implementation: `Source/NXVideo/XFramePicture.cpp:102`

## IsRGB24
- Description: 24-bit RGB 형식인지 확인한다.
- Declaration: `Source/NXVideo/XFramePicture.h:129`
- Implementation: `Source/NXVideo/XFramePicture.cpp:117`

## IsYUV
- Description: YUV 형식인지 확인한다.
- Declaration: `Source/NXVideo/XFramePicture.h:123`
- Implementation: `Source/NXVideo/XFramePicture.cpp:107`

## IsYUV420P
- Description: Planar YUV 4:2:0 형식인지 확인한다.
- Declaration: `Source/NXVideo/XFramePicture.h:117`
- Implementation: `Source/NXVideo/XFramePicture.cpp:95`

## MakeClone
- Description: 화면 프레임 객체와 동일한 객체를 생성하여 반환한다.
- Declaration: `Source/NXVideo/XFramePicture.h:241`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1179`

## PopFrameFromQueue
- Description: 비관리 프레임 큐의 맨 앞에 있는 프레임을 꺼내서 얻는다.
- Declaration: `Source/NXVideo/XFramePicture.h:421`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1684`, `Source/NXVideo/XVideoChannel.cpp:94`

## PushFrameIntoQueue
- Description: 비관리 프레임 큐에 프레임을 추가한다.
- Declaration: `Source/NXVideo/XFramePicture.h:427`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1700`, `Source/NXVideo/XVideoChannel.cpp:96`

## Resize
- Description: 비디오 프레임의 크기를 변경한 새 프레임을 얻는다. RGB 또는 YUV 형식은 원본 프레임 형식 종류의 기본형으로 한다.
- Declaration: `Source/NXVideo/XFramePicture.h:438`, `Source/NXVideo/XFramePicture.h:451`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1744`, `Source/NXVideo/XFramePicture.cpp:1767`

## ResizeCapture
- Description: 비디오 프레임의 크기를 변경하여 그린 프레임 갈무리 버퍼를 얻는다. 바로 활용할 수 있도록 RGB, YUV 형식을 갈무리한다.
- Declaration: `Source/NXVideo/XFramePicture.h:459`, `Source/NXVideo/XFramePicture.h:473`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1790`, `Source/NXVideo/XFramePicture.cpp:1836`

## SaveFrame
- Description: 이 객체의 화면 프레임을 이미지로 저장한다.
- Declaration: `Source/NXVideo/XFramePicture.h:199`, `Source/NXVideo/XFramePicture.h:208`, `Source/NXVideo/XFramePicture.h:220`
- Implementation: `Source/NXVideo/XFramePicture.cpp:338`, `Source/NXVideo/XFramePicture.cpp:577`, `Source/NXVideo/XFramePicture.cpp:631`

## SaveFrameNITF
- Description: 이 객체의 화면 프레임을 EXIF 메타데이터 항목이 추가된 이미지(NITF)로 저장한다.
- Declaration: `Source/NXVideo/XFramePicture.h:227`
- Implementation: `Source/NXVideo/XFramePicture.cpp:897`

## SavePacketData
- Description: 원본 패킷(JPEG) 데이터가 있을 때 이미지 파일로 저장한다.
- Declaration: `Source/NXVideo/XFramePicture.h:236`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1158`

## SetDataBGR
- Description: 프레임 데이터를 BGR 바이트 시퀀스로 바꾼다.
- Declaration: `Source/NXVideo/XFramePicture.h:280`, `Source/NXVideo/XFramePicture.h:287`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1314`, `Source/NXVideo/XFramePicture.cpp:1330`

## SetDataRGB
- Description: 프레임 데이터를 RGB 바이트 시퀀스로 바꾼다.
- Declaration: `Source/NXVideo/XFramePicture.h:265`, `Source/NXVideo/XFramePicture.h:272`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1282`, `Source/NXVideo/XFramePicture.cpp:1298`

## SetDataYUV
- Description: 프레임 데이터를 YUV 바이트 시퀀스로 바꾼다. Y, U, V 데이터가 각각 바이트 배열로 제공되는 YUV[J]420P 형식이어야 한다.
- Declaration: `Source/NXVideo/XFramePicture.h:297`, `Source/NXVideo/XFramePicture.h:306`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1346`, `Source/NXVideo/XFramePicture.cpp:1365`

## SetDataYUVFromBGR
- Description: BGR 바이트 시퀀스로부터 YUV420P 픽처 프레임을 생성한다. 이 경우 입력 데이터의 크기는 프레임 크기와 같아야 한다.
- Declaration: `Source/NXVideo/XFramePicture.h:329`, `Source/NXVideo/XFramePicture.h:336`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1472`, `Source/NXVideo/XFramePicture.cpp:1494`

## SetDataYUVFromBGRA
- Description: BGRA 바이트 시퀀스로부터 YUV420P 픽처 프레임을 생성한다. 이 경우 입력 데이터의 크기는 프레임 크기와 같아야 한다.
- Declaration: `Source/NXVideo/XFramePicture.h:359`, `Source/NXVideo/XFramePicture.h:366`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1516`, `Source/NXVideo/XFramePicture.cpp:1538`

## SetDataYUVFromRGB
- Description: RGB 바이트 시퀀스로부터 YUV420P 픽처 프레임을 생성한다. 이 경우 입력 데이터의 크기는 프레임 크기와 같아야 한다.
- Declaration: `Source/NXVideo/XFramePicture.h:314`, `Source/NXVideo/XFramePicture.h:321`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1384`, `Source/NXVideo/XFramePicture.cpp:1406`

## SetDataYUVFromRGBA
- Description: RGBA 바이트 시퀀스로부터 YUV420P 픽처 프레임을 생성한다. 이 경우 입력 데이터의 크기는 프레임 크기와 같아야 한다.
- Declaration: `Source/NXVideo/XFramePicture.h:344`, `Source/NXVideo/XFramePicture.h:351`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1428`, `Source/NXVideo/XFramePicture.cpp:1450`

## SetHomography
- Description: 프레임의 호모그래피 변환행렬(3x3)을 설정한다.
- Declaration: `Source/NXVideo/XFramePicture.h:399`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1594`

## SetMotion
- Description: 직전 프레임 대비 움직임 변환행렬(3x3)을 설정한다.
- Declaration: `Source/NXVideo/XFramePicture.h:408`
- Implementation: `Source/NXVideo/XFramePicture.cpp:1648`
