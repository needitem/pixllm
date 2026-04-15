---
title: Pixoneer.NXDL.XGrid Methods
aliases:
  - XGrid Methods
  - Pixoneer.NXDL.XGrid
  - XGrid
symbols:
  - XGrid
  - Alloc
  - AllocExact
  - CopySubset
  - FillValue
  - FlipHorz
  - FlipVert
  - Free
  - GetAsReal32
  - GetAsReal64
  - GetColVector
  - GetRowVector
  - GetValue
  - Init
  - IsValid
  - Reform
  - Save
  - SetFromReaL32
  - SetFromReal64
  - SetValue
  - Shift
  - Subset
  - Zerorize
tags:
  - engine
  - methods
  - api
  - pixoneer
  - nxdl
---

# Overview
- Namespace: `Pixoneer.NXDL`
- Type: `XGrid`
- HTML source: `html/Methods_T_Pixoneer_NXDL_XGrid.htm`
- Type declaration: `Source/NXDL/NXDL.h:2400`
- Method count: `22`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.XGrid
type_name: XGrid
namespace: Pixoneer.NXDL
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
## Alloc
- Description: 입력받은 자료 공간 차원 정보 및 데이터 타입에 해당하는 메모리 공간을 할당한다. 만약 이미 할당된 공간이 할당하고자 하는 메모리 공간보다 큰 경우 새롭게 메모리를 할당하지 않고 기존 메모리를 사용하되 파라미터(행 크기, 열 크기, 데이터 타입)만을 변경시킨다.
- Declaration: `Source/NXDL/NXDL.h:2457`
- Implementation: `Source/NXDL/XGrid.cpp:73`

## AllocExact
- Description: 입력받은 자료 공간 차원 정보 및 데이터 타입에 해당하는 메모리 공간을 할당한다. 이 함수를 통해 할당하는 메모리는 Alloc함수와는 다르게 기존에 할당된 메모리를 무조건 해제하고 다시 할당한다.
- Declaration: `Source/NXDL/NXDL.h:2467`
- Implementation: `Source/NXDL/XGrid.cpp:78`

## CopySubset
- Description: 이 객체 데이터의 특정 위치에 새로운 데이터를 복사한다..
- Declaration: `Source/NXDL/NXDL.h:2488`, `Source/NXDL/NXDL.h:2499`, `Source/NXDL/NXDL.h:2508`
- Implementation: `Source/NXDL/XGrid.cpp:93`, `Source/NXDL/XGrid.cpp:122`, `Source/NXDL/XGrid.cpp:143`

## FillValue
- Description: 현재 할당된 데이터 공간을 특정 입력값으로 초기화한다.
- Declaration: `Source/NXDL/NXDL.h:2560`
- Implementation: `Source/NXDL/XGrid.cpp:83`

## FlipHorz
- Description: 데이터를 수평방향으로 뒤집는다.
- Declaration: `Source/NXDL/NXDL.h:2535`
- Implementation: `Source/NXDL/XGrid.cpp:239`

## FlipVert
- Description: 데이터를 수직방향으로 뒤집는다.
- Declaration: `Source/NXDL/NXDL.h:2530`
- Implementation: `Source/NXDL/XGrid.cpp:233`

## Free
- Description: 할당된 메모리를 해제한다.
- Declaration: `Source/NXDL/NXDL.h:2538`
- Implementation: `Source/NXDL/XGrid.cpp:251`

## GetAsReal32
- Description: 특정 위치에 대한 데이터 값을 Real32데이터 형으로 반환한다.
- Declaration: `Source/NXDL/NXDL.h:2578`
- Implementation: `Source/NXDL/XGrid.cpp:308`

## GetAsReal64
- Description: 특정 위치에 대한 데이터 값을 Real64데이터 형으로 반환한다.
- Declaration: `Source/NXDL/NXDL.h:2584`
- Implementation: `Source/NXDL/XGrid.cpp:313`

## GetColVector
- Description: 특정 행에 존재하는 데이터를 추출하여 XGrid객체에 출력한다.
- Declaration: `Source/NXDL/NXDL.h:2553`
- Implementation: `Source/NXDL/XGrid.cpp:287`

## GetRowVector
- Description: 특정 열에 존재하는 데이터를 추출하여 XGrid객체에 출력한다.
- Declaration: `Source/NXDL/NXDL.h:2547`
- Implementation: `Source/NXDL/XGrid.cpp:281`

## GetValue
- Description: 특정 위치에 대한 데이터 값을 Real64데이터 형으로 반환한다.
- Declaration: `Source/NXDL/NXDL.h:2591`, `Source/NXDL/NXDL.h:2601`, `Source/NXDL/NXDL.h:2612`, `Source/NXDL/NXDL.h:2625`, `Source/NXDL/NXDL.h:2635`, `Source/NXDL/NXDL.h:2646`, `Source/NXDL/NXDL.h:2658`, `Source/NXDL/NXDL.h:2672`
- Implementation: `Source/NXDL/XGrid.cpp:318`, `Source/NXDL/XGrid.cpp:327`, `Source/NXDL/XGrid.cpp:337`, `Source/NXDL/XGrid.cpp:348`, `Source/NXDL/XGrid.cpp:360`, `Source/NXDL/XGrid.cpp:369`, `Source/NXDL/XGrid.cpp:379`, `Source/NXDL/XGrid.cpp:390`

## Init
- Description: 내부에 생성된 메모리를 소멸시키고 파라미터들도 초기화한다.
- Declaration: `Source/NXDL/NXDL.h:2446`
- Implementation: `Source/NXDL/XGrid.cpp:68`

## IsValid
- Description: 객체가 유효한지 여부를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:2541`
- Implementation: `Source/NXDL/XGrid.cpp:246`

## Reform
- Description: 이 함수는 배열 정보인 행과 열의 크기를 변형시킨다. 이 함수를 호출시 내부 데이터의 배열이 변경되지는 않고 단순히 행과 열의 파라미터만을 재설정함을 의미한다. 기존 메모리의 크기가 입력된 값보다 작으면 false를 반환한다.
- Declaration: `Source/NXDL/NXDL.h:2477`
- Implementation: `Source/NXDL/XGrid.cpp:88`

## Save
- Description: 데이터를 이진 파일로 저장한다.
- Declaration: `Source/NXDL/NXDL.h:2718`
- Implementation: `Source/NXDL/XGrid.cpp:422`

## SetFromReaL32
- Description: 특정 위치에 대한 데이터 값을 Real32데이터 형으로 설정한다.
- Declaration: `Source/NXDL/NXDL.h:2566`
- Implementation: `Source/NXDL/XGrid.cpp:298`

## SetFromReal64
- Description: 특정 위치에 대한 데이터 값을 Real64데이터 형으로 설정한다.
- Declaration: `Source/NXDL/NXDL.h:2572`
- Implementation: `Source/NXDL/XGrid.cpp:303`

## SetValue
- Description: 특정 위치에 대한 데이터 값을 Real64데이터 형으로 설정한다.
- Declaration: `Source/NXDL/NXDL.h:2680`, `Source/NXDL/NXDL.h:2689`, `Source/NXDL/NXDL.h:2699`, `Source/NXDL/NXDL.h:2711`
- Implementation: `Source/NXDL/XGrid.cpp:402`, `Source/NXDL/XGrid.cpp:407`, `Source/NXDL/XGrid.cpp:412`, `Source/NXDL/XGrid.cpp:417`

## Shift
- Description: 데이터를 X, Y 방향으로 각각 이동한다. 만약 Offset이 5, 8 인경우 (0, 0)의 위치가 (5, 8)가 되며 이동후의 (0, 0)의 위치는 0으로 설정된다. 만약 Offset이 -5, -8 인경우 (5, 8)의 위치가 (0, 0)가 되며 이동후의 제일 마지막 위치의 데이터(차원수 -1, 차원수 -1)는 0으로 설정된다.
- Declaration: `Source/NXDL/NXDL.h:2516`
- Implementation: `Source/NXDL/XGrid.cpp:190`

## Subset
- Description: 데이터의 특정 영역을 읽어서 새로운 XGrid객체를 생성한다.
- Declaration: `Source/NXDL/NXDL.h:2525`
- Implementation: `Source/NXDL/XGrid.cpp:227`

## Zerorize
- Description: 현재 할당된 데이터 공간을 0으로 초기화한다.
- Declaration: `Source/NXDL/NXDL.h:2556`
- Implementation: `Source/NXDL/XGrid.cpp:293`
