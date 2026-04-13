---
title: Pixoneer.NXDL.NXImage.NXImageLayerVectorDisplay Methods
aliases:
  - NXImageLayerVectorDisplay Methods
  - Pixoneer.NXDL.NXImage.NXImageLayerVectorDisplay
  - NXImageLayerVectorDisplay
symbols:
  - NXImageLayerVectorDisplay
  - AddDataSource
  - GetDataSource
  - GetDataSourceAt
  - HitTest
  - MoveDataSource
  - RemoveDataSource
  - RemoveDataSourceAll
  - SetDataSource
  - SetDataSourceUpdateNeeded
  - SetUpdateNeeded
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
- Type: `NXImageLayerVectorDisplay`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXImage_NXImageLayerVectorDisplay.htm`
- Type declaration: `Source/NXImage/NXImageLayerVectorDisplay.h:22`
- Method count: `10`

## AddDataSource
- Description: XvcBase 인스턴스를 추가한다.
- Declaration: `Source/NXImage/NXImageLayerVectorDisplay.h:57`
- Implementation: `Source/NXImage/NXImageLayerVectorDisplay.cpp:106`

## GetDataSource
- Description: 도시를 위한 객체를 가져온다. XvcBase 객체 리스트 중 첫번째 XvcBase 객체를 가져온다. (XvcBase는 하나 이상의 레이어로 구성되며, 레이어(XvcLayer)에는 여러 개의 객체가 있다.)
- Declaration: `Source/NXImage/NXImageLayerVectorDisplay.h:46`
- Implementation: `Source/NXImage/NXImageLayerVectorDisplay.cpp:53`

## GetDataSourceAt
- Description: 해당 인덱스의 XvcBase 객체를 가져온다.
- Declaration: `Source/NXImage/NXImageLayerVectorDisplay.h:74`
- Implementation: `Source/NXImage/NXImageLayerVectorDisplay.cpp:133`

## HitTest
- Description: 특정 위치에 해당 객체의 hit-testing을 수행한다.
- Declaration: `Source/NXImage/NXImageLayerVectorDisplay.h:42`
- Implementation: `Source/NXImage/NXImageLayerVectorDisplay.cpp:85`

## MoveDataSource
- Description: XvcBase 객체 리스트의 도시 순서를 변경한다.
- Declaration: `Source/NXImage/NXImageLayerVectorDisplay.h:69`
- Implementation: `Source/NXImage/NXImageLayerVectorDisplay.cpp:127`

## RemoveDataSource
- Description: XvcBase 객체 리스트에서 지정한 객체를 삭제한다.
- Declaration: `Source/NXImage/NXImageLayerVectorDisplay.h:61`
- Implementation: `Source/NXImage/NXImageLayerVectorDisplay.cpp:113`

## RemoveDataSourceAll
- Description: XvcBase 객체 도시 리스트 전체를 삭제한다.
- Declaration: `Source/NXImage/NXImageLayerVectorDisplay.h:64`
- Implementation: `Source/NXImage/NXImageLayerVectorDisplay.cpp:121`

## SetDataSource
- Description: XvcBase 인스턴스를 사용자 정의로 설정한다. 외부 XvcBase를 설정하면 새로이 생성되는 객체는 외부 XvcBase에 추가된다. SetDataSource() 사용시 기존 XvcBase 객체 리스트는 모두 삭제되고 매개변수로 넘겨받은 XvcBase 객체만 추가된다.
- Declaration: `Source/NXImage/NXImageLayerVectorDisplay.h:52`
- Implementation: `Source/NXImage/NXImageLayerVectorDisplay.cpp:62`

## SetDataSourceUpdateNeeded
- Description: 지정한 벡터 객체만 갱신하도록 한다.
- Declaration: `Source/NXImage/NXImageLayerVectorDisplay.h:86`
- Implementation: `Source/NXImage/NXImageLayerVectorDisplay.cpp:77`

## SetUpdateNeeded
- Description: 전체 XvcBase 객체 리스트를 갱신하도록 한다.
- Declaration: `Source/NXImage/NXImageLayerVectorDisplay.h:81`
- Implementation: `Source/NXImage/NXImageLayerVectorDisplay.cpp:70`
