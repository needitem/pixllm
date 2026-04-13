---
title: Pixoneer.NXDL.NRS.XDMBand Methods
aliases:
  - XDMBand Methods
  - Pixoneer.NXDL.NRS.XDMBand
  - XDMBand
symbols:
  - XDMBand
  - AddGIS
  - CalcSubsetHistogram
  - CalcSubsetStatistics
  - FindGISFromID
  - GetBandDate
  - GetBandMax
  - GetBandMean
  - GetBandMin
  - GetBandStdDev
  - GetBandTime
  - GetBoundRect
  - GetCenter
  - GetEPOTCompressionType
  - GetGISAt
  - GetGISColorTable
  - GetHighestLevelForTarget
  - GetHistogram
  - GetLevel
  - GetNativePtr
  - GetNumOfGIS
  - GetPixelSize
  - GetSize
  - GetUpperLeft
  - IsDataTypeComplex
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
- Type: `XDMBand`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NRS_XDMBand.htm`
- Type declaration: `Source/NXDLrs/NXDLrs.h:590`
- Method count: `47`

## AddGIS
- Description: XRSGIS 인스턴스를 추가한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:888`
- Implementation: `Source/NXDLrs/XDMBand.cpp:352`

## CalcSubsetHistogram
- Description: LOD 레벨값과 영역정보에 대한 영상 히스토그램을 계산한다. 히스토그램 구간 개수를 설정하여 히스토그램을 계산한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1110`, `Source/NXDLrs/NXDLrs.h:1146`
- Implementation: `Source/NXDLrs/XDMBand.cpp:1038`, `Source/NXDLrs/XDMBand.cpp:1098`

## CalcSubsetStatistics
- Description: LOD 레벨값과 영역정보에 대한 영상 데이터 통계값을 산출한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1051`, `Source/NXDLrs/NXDLrs.h:1066`
- Implementation: `Source/NXDLrs/XDMBand.cpp:1002`, `Source/NXDLrs/XDMBand.cpp:1068`

## FindGISFromID
- Description: 밴드에 있는 XRSGIS 인스턴스 중에서 매개변수로 입력되는 ID에 해당하는 인스턴스를 찾는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:898`
- Implementation: `Source/NXDLrs/XDMBand.cpp:390`

## GetBandDate
- Description: 영상 획득된 날짜를 얻는다. 이 정보는 Import시 원본 메타데이터 및 정보를 읽어 헤더 파일에 저장한 값이다.
- Declaration: `Source/NXDLrs/NXDLrs.h:709`
- Implementation: `Source/NXDLrs/XDMBand.cpp:755`

## GetBandMax
- Description: 영상 데이터 DN 최댓값을 가져온다.(NullValue는 제외한다.) 영상의 데이터 타입이 Complex 타입일 경우, Complex output type에 해당하는 최댓값을 가져온다. Complex output type을 Magnitude로 설정하면 BandMax값을 가져온다. Complex output type을 Real, Imaginary, Phase중 하나로 설정하면 각 output type에 해당하는 최댓값을 가져올 수 있다.
- Declaration: `Source/NXDLrs/NXDLrs.h:850`
- Implementation: `Source/NXDLrs/XDMBand.cpp:893`

## GetBandMean
- Description: 영상 데이터 DN 평균값을 가져온다 영상의 데이터 타입이 Complex 타입일 경우, Complex output type에 해당하는 평균값을 가져온다. Complex output type을 Magnitude로 설정하면 BandMean값을 가져온다. Complex output type을 Real, Imaginary, Phase중 하나로 설정하면 각 output type에 해당하는 평균값을 가져올 수 있다.
- Declaration: `Source/NXDLrs/NXDLrs.h:860`
- Implementation: `Source/NXDLrs/XDMBand.cpp:910`

## GetBandMin
- Description: 영상 데이터 DN 최솟값을 가져온다.(NullValue는 제외한다.) 영상의 데이터 타입이 Complex 타입일 경우, Complex output type에 해당하는 최솟값을 가져온다. Complex output type을 Magnitude로 설정하면 BandMin값을 가져온다. Complex output type을 Real, Imaginary, Phase중 하나로 설정하면 각 output type에 해당하는 최솟값을 가져올 수 있다.
- Declaration: `Source/NXDLrs/NXDLrs.h:840`
- Implementation: `Source/NXDLrs/XDMBand.cpp:875`

## GetBandStdDev
- Description: 영상 데이터 DN 표준편차를 가져온다 영상의 데이터 타입이 Complex 타입일 경우, Complex output type에 해당하는 표준편차를 가져온다. Complex output type을 Magnitude로 설정하면 BandStdDev값을 가져온다. Complex output type을 Real, Imaginary, Phase중 하나로 설정하면 각 output type에 해당하는 표준편차를 가져올 수 있다.
- Declaration: `Source/NXDLrs/NXDLrs.h:870`
- Implementation: `Source/NXDLrs/XDMBand.cpp:927`

## GetBandTime
- Description: 영상 획득된 시간을 얻는다. 이 정보는 Import시 원본 메타데이터 및 정보를 읽어 헤더 파일에 저장한 값이다.
- Declaration: `Source/NXDLrs/NXDLrs.h:715`
- Implementation: `Source/NXDLrs/XDMBand.cpp:773`

## GetBoundRect
- Description: 영상 경계역역에 대한 세계 좌표를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:695`
- Implementation: `Source/NXDLrs/XDMBand.cpp:187`

## GetCenter
- Description: 영상 밴드의 중심 좌표를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:670`
- Implementation: `Source/NXDLrs/XDMBand.cpp:211`

## GetEPOTCompressionType
- Description: 밴드의 영상의 압축 형태를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:638`
- Implementation: `Source/NXDLrs/XDMBand.cpp:712`

## GetGISAt
- Description: 입력된 인덱스에 대응하는 XRSGIS 인스턴스를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:893`
- Implementation: `Source/NXDLrs/XDMBand.cpp:369`

## GetGISColorTable
- Description: XRSGIS 객체에 설정된 ColorTable을 얻는다. 이값은 복사해서 얻기 때문에 여기의 값이 바뀌어도 Band 내의 XRSGIS값에 대한 Color값이 바뀌지 않는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:915`
- Implementation: `Source/NXDLrs/XDMBand.cpp:445`

## GetHighestLevelForTarget
- Description: Target 영역에 특정 영역의 영상을 도시하기 위한 최대 레벨을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1008`
- Implementation: `Source/NXDLrs/XDMBand.cpp:698`

## GetHistogram
- Description: 영상 데이터 히스토그램을 가져온다 영상의 데이터 타입이 Complex 타입일 경우, Complex output type에 해당하는 히스토그램을 가져온다. Complex output type을 Magnitude로 설정하면 Histogram값을 가져온다. Complex output type을 Real, Imaginary, Phase중 하나로 설정하면 각 output type에 해당하는 히스토그램을 가져올 수 있다.
- Declaration: `Source/NXDLrs/NXDLrs.h:880`
- Implementation: `Source/NXDLrs/XDMBand.cpp:945`

## GetLevel
- Description: 최대 LOD 레벨을 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:998`
- Implementation: `Source/NXDLrs/XDMBand.cpp:692`

## GetNativePtr
- Description: XDMBand의 원본 비관리 객체 포인터를 반환한다. C#에서 사용 불가.
- Declaration: `Source/NXDLrs/NXDLrs.h:613`
- Implementation: `Source/NXDLrs/XDMBand.cpp:76`

## GetNumOfGIS
- Description: XDMBand 객체에 포함된 XRSGIS객체의 수를 얻는다. XRSGIS 객체는 분류(Classification) 후에 정보를 담기 위해 저장한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:884`
- Implementation: `Source/NXDLrs/XDMBand.cpp:344`

## GetPixelSize
- Description: 영상에 대한 한 픽셀의 공간 크기를 얻는다. 즉, 하나의 픽셀에 대한 픽셀 거리를 얻는다. 좌표계가 있는 파일에 대해 위경도 좌표계인 경우 단위는 degree이고, 그렇지 않은 경우에는 meter이다. 좌표계가 없는 파일은 픽셀 단위이다.
- Declaration: `Source/NXDLrs/NXDLrs.h:660`
- Implementation: `Source/NXDLrs/XDMBand.cpp:103`

## GetSize
- Description: 밴드의 row와 column 방향 크기를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:634`
- Implementation: `Source/NXDLrs/XDMBand.cpp:118`

## GetUpperLeft
- Description: 좌상단 지리좌표를 얻는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:648`
- Implementation: `Source/NXDLrs/XDMBand.cpp:177`

## IsDataTypeComplex
- Description: 밴드 데이터 타입이 Complex 타입인지 여부를 확인한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1012`
- Implementation: `Source/NXDLrs/XDMBand.cpp:704`

## IsEqual
- Description: 입력 밴드 인스턴스와 동일한지를 검사한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:1227`
- Implementation: `Source/NXDLrs/XDMBand.cpp:628`

## PixelToWorld
- Description: 밴드 정보 기반으로 화소 좌표를 지리 좌표로 변환한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:619`
- Implementation: `Source/NXDLrs/XDMBand.cpp:81`

## ReadLineH
- Description: 입력된 Level과 Row 위치에 대한 화소들을 모두 읽어 XGrid객체로 반환한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:923`, `Source/NXDLrs/NXDLrs.h:932`
- Implementation: `Source/NXDLrs/XDMBand.cpp:644`, `Source/NXDLrs/XDMBand.cpp:650`

## ReadLineV
- Description: 입력된 Level과 Column 위치에 대한 화소들을 모두 읽어 XGrid객체로 반환한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:939`, `Source/NXDLrs/NXDLrs.h:948`
- Implementation: `Source/NXDLrs/XDMBand.cpp:656`, `Source/NXDLrs/XDMBand.cpp:662`

## ReadPixel
- Description: 입력된 화소의 위치(XLZ, YLZ)로부터 픽셀값을 읽는다. 출력값을 무조건 double형으로 변환하여 반환한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:955`, `Source/NXDLrs/NXDLrs.h:961`
- Implementation: `Source/NXDLrs/XDMBand.cpp:637`, `Source/NXDLrs/XDMBand.cpp:668`

## ReadProfile
- Description: 2차원 영상 영역에서 두 점 사이 Profile을 읽는다.
- Declaration: `Source/NXDLrs/NXDLrs.h:982`, `Source/NXDLrs/NXDLrs.h:994`
- Implementation: `Source/NXDLrs/XDMBand.cpp:680`, `Source/NXDLrs/XDMBand.cpp:686`

## ReadSubset
- Description: 특정 영역을 읽어서 반환한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:971`
- Implementation: `Source/NXDLrs/XDMBand.cpp:674`

## RemoveAllGIS
- Description: XRSGIS 배열의 모든 XRSGIS 객체를 삭제한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:910`
- Implementation: `Source/NXDLrs/XDMBand.cpp:437`

## RemoveGISAt
- Description: XRSGIS 배열로부터 입력된 인덱스에 대응하는 XRSGIS 인스턴스를 삭제한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:907`
- Implementation: `Source/NXDLrs/XDMBand.cpp:429`

## SetBandDate
- Description: 영상 획득된 날짜를 저장한다.(예:20180101 - 2018년 01월 01일을 의미한다. YYMMDD)
- Declaration: `Source/NXDLrs/NXDLrs.h:699`
- Implementation: `Source/NXDLrs/XDMBand.cpp:743`

## SetBandMax
- Description: 영상 데이터 DN 최댓값을 설정한다.(NullValue는 제외한다.) 영상의 데이터 타입이 Complex 타입일 경우, Complex output type에 해당하는 최댓값을 설정한다. Complex output type을 Magnitude로 설정하면 val값은 BandMax에 설정된다. Complex output type을 Real, Imaginary, Phase중 하나로 설정하면 각 output type에 해당하는 최댓값을 설정할 수 있다.
- Declaration: `Source/NXDLrs/NXDLrs.h:800`
- Implementation: `Source/NXDLrs/XDMBand.cpp:807`

## SetBandMean
- Description: 영상 데이터 DN 평균값을 설정한다. 영상의 데이터 타입이 Complex 타입일 경우, Complex output type에 해당하는 평균값을 설정한다. Complex output type을 Magnitude로 설정하면 val값은 BandMean에 설정된다. Complex output type을 Real, Imaginary, Phase중 하나로 설정하면 각 output type에 해당하는 평균값을 설정할 수 있다.
- Declaration: `Source/NXDLrs/NXDLrs.h:810`
- Implementation: `Source/NXDLrs/XDMBand.cpp:823`

## SetBandMin
- Description: 영상 데이터 DN 최솟값을 설정한다.(NullValue는 제외한다.) 영상의 데이터 타입이 Complex 타입일 경우, Complex output type에 해당하는 최솟값을 설정한다. Complex output type을 Magnitude로 설정하면 val값은 BandMin에 설정된다. Complex output type을 Real, Imaginary, Phase중 하나로 설정하면 각 output type에 해당하는 최솟값을 설정할 수 있다.
- Declaration: `Source/NXDLrs/NXDLrs.h:790`
- Implementation: `Source/NXDLrs/XDMBand.cpp:791`

## SetBandStdDev
- Description: 영상 데이터 DN 표준편차를 설정한다. 영상의 데이터 타입이 Complex 타입일 경우, Complex output type에 해당하는 표준편차를 설정한다. Complex output type을 Magnitude로 설정하면 val값은 BandStdDev에 설정된다. Complex output type을 Real, Imaginary, Phase중 하나로 설정하면 각 output type에 해당하는 표준편차를 설정할 수 있다.
- Declaration: `Source/NXDLrs/NXDLrs.h:820`
- Implementation: `Source/NXDLrs/XDMBand.cpp:839`

## SetBandTime
- Description: 영상 획득된 시간을 저장한다. (예:123456 - 12시 34분 56초를 의미한다. hhmmss)
- Declaration: `Source/NXDLrs/NXDLrs.h:703`
- Implementation: `Source/NXDLrs/XDMBand.cpp:749`

## SetBoundRect
- Description: 영상 경계역역에 대한 세계 좌표를 설정한다. 입력 매개변수를 통해 내부적으로 영상의 크기가 결정된다.
- Declaration: `Source/NXDLrs/NXDLrs.h:679`, `Source/NXDLrs/NXDLrs.h:688`
- Implementation: `Source/NXDLrs/XDMBand.cpp:531`, `Source/NXDLrs/XDMBand.cpp:539`

## SetCenter
- Description: 영상 밴드의 중심 좌표를 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:665`
- Implementation: `Source/NXDLrs/XDMBand.cpp:563`

## SetGISAt
- Description: 입력된 인덱스에 XRSGIS 인스턴스를 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:903`
- Implementation: `Source/NXDLrs/XDMBand.cpp:411`

## SetHistogram
- Description: 영상 데이터 히스토그램을 설정한다. 영상의 데이터 타입이 Complex 타입일 경우, Complex output type에 해당하는 히스토그램을 설정한다. Complex output type을 Magnitude로 설정하면 val값은 Histogram에 설정된다. Complex output type을 Real, Imaginary, Phase중 하나로 설정하면 각 output type에 해당하는 히스토그램을 설정할 수 있다.
- Declaration: `Source/NXDLrs/NXDLrs.h:830`
- Implementation: `Source/NXDLrs/XDMBand.cpp:854`

## SetPixelSize
- Description: 영상의 한 픽셀 공간 크기를 설정한다. 즉, 하나의 픽셀에 대한 픽셀 거리(공간 해상도)를 설정한다. 좌표계가 있는 파일에 대해 위경도 좌표계인 경우 단위는 degree이고, 그렇지 않은 경우에는 meter이다. 좌표계가 없는 파일은 픽셀 단위이다.
- Declaration: `Source/NXDLrs/NXDLrs.h:654`
- Implementation: `Source/NXDLrs/XDMBand.cpp:470`

## SetSize
- Description: 밴드의 row와 column 방향 크기를 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:629`
- Implementation: `Source/NXDLrs/XDMBand.cpp:112`

## SetUpperLeft
- Description: 좌상단 지리좌표를 설정한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:643`
- Implementation: `Source/NXDLrs/XDMBand.cpp:462`

## WorldToPixel
- Description: 밴드 정보 기반으로 지리 좌표를 화소 좌표로 변환한다.
- Declaration: `Source/NXDLrs/NXDLrs.h:624`
- Implementation: `Source/NXDLrs/XDMBand.cpp:91`
