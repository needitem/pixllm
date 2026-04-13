---
title: Pixoneer.NXDL.NRS.XROI Methods
aliases:
  - XROI Methods
  - Pixoneer.NXDL.NRS.XROI
  - XROI
symbols:
  - XROI
  - AddVert
  - CalcStatistics
  - GetCorrelation
  - GetCovariance
  - GetCovarianceInverse
  - GetHistogram
  - GetMax
  - GetMean
  - GetMin
  - GetRange
  - GetStd
  - GetSum
  - GetSumProduct
  - GetSumSquare
  - GetVertAt
  - GetVertSize
  - IsCalculated
  - RemoveVertAll
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
- Type: `XROI`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XROI.htm`
- Type declaration: `Source/NXDLrs/NXDLrs.h:237`
- Method count: `18`

## AddVert
- Description: ROI를 생성하기 위한 정점를 추가한다. 폴리곤의 각 정점이 이에 해당한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:259`
- Implementation: `Source/NXDLrs/XROI.cpp:55`

## CalcStatistics
- Description: 입력되는 Band의 리스트에 해당하는 통계치를 계산한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:346`
- Implementation: `Source/NXDLrs/XROI.cpp:229`

## GetCorrelation
- Description: Band Index의 두 영상 밴드에 대한 ROI 영역 내 상관도값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:311`
- Implementation: `Source/NXDLrs/XROI.cpp:179`

## GetCovariance
- Description: Band Index의 두 영상 밴드에 대한 ROI 영역 내 공분산값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:299`
- Implementation: `Source/NXDLrs/XROI.cpp:163`

## GetCovarianceInverse
- Description: Band Index의 두 영상 밴드에 대한 ROI 영역 내 공분산 역수값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:305`
- Implementation: `Source/NXDLrs/XROI.cpp:171`

## GetHistogram
- Description: Band Index의 영상 밴드에 대한 ROI 영역 내 히스토그램 값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:317`
- Implementation: `Source/NXDLrs/XROI.cpp:187`

## GetMax
- Description: Band Index의 영상 밴드에 대한 ROI 영역 내 최댓값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:283`
- Implementation: `Source/NXDLrs/XROI.cpp:139`

## GetMean
- Description: Band Index의 영상 밴드에 대한 ROI 영역 내 평균값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:288`
- Implementation: `Source/NXDLrs/XROI.cpp:147`

## GetMin
- Description: Band Index의 영상 밴드에 대한 ROI 영역 내 최솟값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:278`
- Implementation: `Source/NXDLrs/XROI.cpp:131`

## GetRange
- Description: ROI의 경계 영역값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:340`
- Implementation: `Source/NXDLrs/XROI.cpp:219`

## GetStd
- Description: Band Index의 영상 밴드에 대한 ROI 영역 내 표준편차값을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:293`
- Implementation: `Source/NXDLrs/XROI.cpp:155`

## GetSum
- Description: Band Index의 영상 밴드에 대한 ROI 영역 내 합을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:322`
- Implementation: `Source/NXDLrs/XROI.cpp:195`

## GetSumProduct
- Description: Band 화소간의 곱에 대한 합을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:333`
- Implementation: `Source/NXDLrs/XROI.cpp:211`

## GetSumSquare
- Description: Band Index의 영상 밴드에 대한 ROI 영역 내 제곱합을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:327`
- Implementation: `Source/NXDLrs/XROI.cpp:203`

## GetVertAt
- Description: ROI를 생성하기 위해 추가된 정점 중 해당 Index에 대한 정점을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:264`
- Implementation: `Source/NXDLrs/XROI.cpp:63`

## GetVertSize
- Description: ROI를 생성하기 위해 추가된 총 정점 개수를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:268`
- Implementation: `Source/NXDLrs/XROI.cpp:75`

## IsCalculated
- Description: ROI 통계치가 계산되었는지 여부를 반환한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:253`
- Implementation: `Source/NXDLrs/XROI.cpp:47`

## RemoveVertAll
- Description: 모든 정점을 삭제한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:271`
- Implementation: `Source/NXDLrs/XROI.cpp:81`
