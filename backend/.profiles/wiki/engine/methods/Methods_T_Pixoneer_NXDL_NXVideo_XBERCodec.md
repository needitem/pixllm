---
title: Pixoneer.NXDL.NXVideo.XBERCodec Methods
aliases:
  - XBERCodec Methods
  - Pixoneer.NXDL.NXVideo.XBERCodec
  - XBERCodec
symbols:
  - XBERCodec
  - Decode
  - DecodeBER_Length
  - DecodeBER_OID
  - DecodeVL
  - Encode
  - EncodeBER_Length
  - EncodeBER_OID
  - EncodeVL
  - GetLengthEncodingBytes
  - GetMappedValue
  - GetOIDEncodingBytes
  - IMAP_Backward
  - IMAP_Length
  - IMAPA_Forward
  - IMAPB_Forward
  - SetMappedValue
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
- Type: `XBERCodec`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_XBERCodec.htm`
- Type declaration: `Source/NXVideo/XUasMetadata.h:906`
- Method count: `16`

## Decode
- Description: 부호 없는 8비트 정수값을 디코딩한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:937`, `Source/NXVideo/XUasMetadata.h:944`, `Source/NXVideo/XUasMetadata.h:951`, `Source/NXVideo/XUasMetadata.h:958`, `Source/NXVideo/XUasMetadata.h:965`, `Source/NXVideo/XUasMetadata.h:972`, `Source/NXVideo/XUasMetadata.h:979`, `Source/NXVideo/XUasMetadata.h:986`, `Source/NXVideo/XUasMetadata.h:993`, `Source/NXVideo/XUasMetadata.h:1005`, `Source/NXVideo/XUasMetadata.h:1017`, `Source/NXVideo/XUasMetadata.h:1029`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:355`, `Source/NXVideo/XUasMetadata.cpp:858`, `Source/NXVideo/XUasMetadata.cpp:864`, `Source/NXVideo/XUasMetadata.cpp:868`, `Source/NXVideo/XUasMetadata.cpp:873`, `Source/NXVideo/XUasMetadata.cpp:878`, `Source/NXVideo/XUasMetadata.cpp:883`, `Source/NXVideo/XUasMetadata.cpp:888`, `Source/NXVideo/XUasMetadata.cpp:893`, `Source/NXVideo/XUasMetadata.cpp:898`, `Source/NXVideo/XUasMetadata.cpp:903`, `Source/NXVideo/XUasMetadata.cpp:908`, `Source/NXVideo/XUasMetadata.cpp:913`, `Source/NXVideo/XUasMetadata.cpp:918`, `Source/NXVideo/XUasMetadata.cpp:923`, `Source/NXVideo/XUasMetadata.cpp:928`, `Source/NXVideo/XUasMetadata.cpp:933`, `Source/NXVideo/XUasMetadata.cpp:938`, `Source/NXVideo/XUasMetadata.cpp:943`, `Source/NXVideo/XUasMetadata.cpp:948`, `Source/NXVideo/XUasMetadata.cpp:955`, `Source/NXVideo/XUasMetadata.cpp:960`, `Source/NXVideo/XUasMetadata.cpp:967`, `Source/NXVideo/XUasMetadata.cpp:972`, `Source/NXVideo/XUasMetadata.cpp:979`

## DecodeBER_Length
- Description: 길이 형식의 값을 디코딩한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:928`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:848`, `Source/NXVideo/XUasMetadata.cpp:853`

## DecodeBER_OID
- Description: 태그(Tag)와 같이 식별자(ID) 형식의 값을 디코딩한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:914`, `Source/NXVideo/XUasMetadata.h:921`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:347`, `Source/NXVideo/XUasMetadata.cpp:828`, `Source/NXVideo/XUasMetadata.cpp:833`, `Source/NXVideo/XUasMetadata.cpp:838`, `Source/NXVideo/XUasMetadata.cpp:843`

## DecodeVL
- Description: 가변 길이 정수값을 부호 없는 8비트 정수로 디코딩한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1267`, `Source/NXVideo/XUasMetadata.h:1275`, `Source/NXVideo/XUasMetadata.h:1283`, `Source/NXVideo/XUasMetadata.h:1291`, `Source/NXVideo/XUasMetadata.h:1299`, `Source/NXVideo/XUasMetadata.h:1307`, `Source/NXVideo/XUasMetadata.h:1315`, `Source/NXVideo/XUasMetadata.h:1323`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1173`, `Source/NXVideo/XUasMetadata.cpp:1178`, `Source/NXVideo/XUasMetadata.cpp:1183`, `Source/NXVideo/XUasMetadata.cpp:1188`, `Source/NXVideo/XUasMetadata.cpp:1193`, `Source/NXVideo/XUasMetadata.cpp:1198`, `Source/NXVideo/XUasMetadata.cpp:1203`, `Source/NXVideo/XUasMetadata.cpp:1208`, `Source/NXVideo/XUasMetadata.cpp:1213`, `Source/NXVideo/XUasMetadata.cpp:1218`, `Source/NXVideo/XUasMetadata.cpp:1223`, `Source/NXVideo/XUasMetadata.cpp:1228`, `Source/NXVideo/XUasMetadata.cpp:1233`, `Source/NXVideo/XUasMetadata.cpp:1238`, `Source/NXVideo/XUasMetadata.cpp:1243`, `Source/NXVideo/XUasMetadata.cpp:1248`

## Encode
- Description: 부호 없는 8비트 정수값을 바이트 버퍼에 인코딩하여 추가한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1062`, `Source/NXVideo/XUasMetadata.h:1069`, `Source/NXVideo/XUasMetadata.h:1076`, `Source/NXVideo/XUasMetadata.h:1083`, `Source/NXVideo/XUasMetadata.h:1090`, `Source/NXVideo/XUasMetadata.h:1097`, `Source/NXVideo/XUasMetadata.h:1104`, `Source/NXVideo/XUasMetadata.h:1111`, `Source/NXVideo/XUasMetadata.h:1118`, `Source/NXVideo/XUasMetadata.h:1129`, `Source/NXVideo/XUasMetadata.h:1140`, `Source/NXVideo/XUasMetadata.h:1151`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1008`, `Source/NXVideo/XUasMetadata.cpp:1015`, `Source/NXVideo/XUasMetadata.cpp:1018`, `Source/NXVideo/XUasMetadata.cpp:1022`, `Source/NXVideo/XUasMetadata.cpp:1025`, `Source/NXVideo/XUasMetadata.cpp:1029`, `Source/NXVideo/XUasMetadata.cpp:1032`, `Source/NXVideo/XUasMetadata.cpp:1036`, `Source/NXVideo/XUasMetadata.cpp:1039`, `Source/NXVideo/XUasMetadata.cpp:1043`, `Source/NXVideo/XUasMetadata.cpp:1046`, `Source/NXVideo/XUasMetadata.cpp:1050`, `Source/NXVideo/XUasMetadata.cpp:1053`, `Source/NXVideo/XUasMetadata.cpp:1057`, `Source/NXVideo/XUasMetadata.cpp:1060`, `Source/NXVideo/XUasMetadata.cpp:1064`, `Source/NXVideo/XUasMetadata.cpp:1067`, `Source/NXVideo/XUasMetadata.cpp:1071`, `Source/NXVideo/XUasMetadata.cpp:1074`, `Source/NXVideo/XUasMetadata.cpp:1080`, `Source/NXVideo/XUasMetadata.cpp:1083`, `Source/NXVideo/XUasMetadata.cpp:1089`, `Source/NXVideo/XUasMetadata.cpp:1092`, `Source/NXVideo/XUasMetadata.cpp:1098`

## EncodeBER_Length
- Description: 길이 데이터를 바이트 버퍼에 인코딩하여 추가한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1053`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:991`, `Source/NXVideo/XUasMetadata.cpp:1001`, `Source/NXVideo/XUasMetadata.cpp:1005`

## EncodeBER_OID
- Description: 식별자를 바이트 버퍼에 인코딩하여 추가한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1046`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:986`, `Source/NXVideo/XUasMetadata.cpp:994`, `Source/NXVideo/XUasMetadata.cpp:998`

## EncodeVL
- Description: 부호 없는 8비트 정수값을 가변 길이로 바이트 버퍼에 인코딩하여 추가한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1331`, `Source/NXVideo/XUasMetadata.h:1339`, `Source/NXVideo/XUasMetadata.h:1347`, `Source/NXVideo/XUasMetadata.h:1355`, `Source/NXVideo/XUasMetadata.h:1363`, `Source/NXVideo/XUasMetadata.h:1371`, `Source/NXVideo/XUasMetadata.h:1379`, `Source/NXVideo/XUasMetadata.h:1387`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1253`, `Source/NXVideo/XUasMetadata.cpp:1257`, `Source/NXVideo/XUasMetadata.cpp:1260`, `Source/NXVideo/XUasMetadata.cpp:1264`, `Source/NXVideo/XUasMetadata.cpp:1267`, `Source/NXVideo/XUasMetadata.cpp:1271`, `Source/NXVideo/XUasMetadata.cpp:1274`, `Source/NXVideo/XUasMetadata.cpp:1278`, `Source/NXVideo/XUasMetadata.cpp:1281`, `Source/NXVideo/XUasMetadata.cpp:1285`, `Source/NXVideo/XUasMetadata.cpp:1288`, `Source/NXVideo/XUasMetadata.cpp:1292`, `Source/NXVideo/XUasMetadata.cpp:1295`, `Source/NXVideo/XUasMetadata.cpp:1299`, `Source/NXVideo/XUasMetadata.cpp:1302`, `Source/NXVideo/XUasMetadata.cpp:1306`

## GetLengthEncodingBytes
- Description: 길이 데이터의 인코딩 길이를 구한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1039`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:989`

## GetMappedValue
- Description: 최대, 최소 범위로 인코딩된 부호 없는 8비트 정수값을 실제 값으로 디코딩한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1160`, `Source/NXVideo/XUasMetadata.h:1169`, `Source/NXVideo/XUasMetadata.h:1178`, `Source/NXVideo/XUasMetadata.h:1187`, `Source/NXVideo/XUasMetadata.h:1196`, `Source/NXVideo/XUasMetadata.h:1205`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1101`, `Source/NXVideo/XUasMetadata.cpp:1103`, `Source/NXVideo/XUasMetadata.cpp:1106`, `Source/NXVideo/XUasMetadata.cpp:1108`, `Source/NXVideo/XUasMetadata.cpp:1111`, `Source/NXVideo/XUasMetadata.cpp:1113`, `Source/NXVideo/XUasMetadata.cpp:1116`, `Source/NXVideo/XUasMetadata.cpp:1118`, `Source/NXVideo/XUasMetadata.cpp:1121`, `Source/NXVideo/XUasMetadata.cpp:1123`, `Source/NXVideo/XUasMetadata.cpp:1126`, `Source/NXVideo/XUasMetadata.cpp:1128`

## GetOIDEncodingBytes
- Description: 식별자의 인코딩 길이를 구한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1034`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:984`

## IMAP_Backward
- Description: 정수 대응 실수 표현(IMAP)으로 인코딩된 실수값을 디코딩한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1404`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1314`, `Source/NXVideo/XUasMetadata.cpp:1320`

## IMAP_Length
- Description: 정수 대응 실수 표현(Floating Point to Integer Mapping, IMAP)의 인코딩 길이를 구한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1394`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1309`, `Source/NXVideo/XUasMetadata.cpp:1311`

## IMAPA_Forward
- Description: 실수 범위와 정밀도에 맞춰 주어진 실수값을 정수 대응 실수 표현(IMAPA)으로 인코딩하여 바이트 버퍼에 추가한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1414`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1325`, `Source/NXVideo/XUasMetadata.cpp:1329`

## IMAPB_Forward
- Description: 실수 범위와 인코딩 길이에 맞춰 주어진 실수값을 정수 대응 실수 표현(IMAPB)으로 인코딩하여 바이트 버퍼에 추가한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1424`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1332`, `Source/NXVideo/XUasMetadata.cpp:1336`

## SetMappedValue
- Description: 실수값을 최대, 최소 범위에서 상대적 위치를 나타내는 부호 없는 8비트 정수값으로 인코딩한다.
- Declaration: `Source/NXVideo/XUasMetadata.h:1214`, `Source/NXVideo/XUasMetadata.h:1223`, `Source/NXVideo/XUasMetadata.h:1232`, `Source/NXVideo/XUasMetadata.h:1241`, `Source/NXVideo/XUasMetadata.h:1250`, `Source/NXVideo/XUasMetadata.h:1259`
- Implementation: `Source/NXVideo/XUasMetadata.cpp:1131`, `Source/NXVideo/XUasMetadata.cpp:1134`, `Source/NXVideo/XUasMetadata.cpp:1138`, `Source/NXVideo/XUasMetadata.cpp:1141`, `Source/NXVideo/XUasMetadata.cpp:1145`, `Source/NXVideo/XUasMetadata.cpp:1148`, `Source/NXVideo/XUasMetadata.cpp:1152`, `Source/NXVideo/XUasMetadata.cpp:1155`, `Source/NXVideo/XUasMetadata.cpp:1159`, `Source/NXVideo/XUasMetadata.cpp:1162`, `Source/NXVideo/XUasMetadata.cpp:1166`, `Source/NXVideo/XUasMetadata.cpp:1169`
