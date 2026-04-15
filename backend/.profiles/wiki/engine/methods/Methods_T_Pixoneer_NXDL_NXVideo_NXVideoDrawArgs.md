---
title: Pixoneer.NXDL.NXVideo.NXVideoDrawArgs Methods
aliases:
  - NXVideoDrawArgs Methods
  - Pixoneer.NXDL.NXVideo.NXVideoDrawArgs
  - NXVideoDrawArgs
symbols:
  - NXVideoDrawArgs
  - InvalidatePtr
  - SetPtr
  - SpaceToWorld
  - WorldToSpace
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
- Type: `NXVideoDrawArgs`
- HTML source: `html/Methods_T_Pixoneer_NXDL_NXVideo_NXVideoDrawArgs.htm`
- Type declaration: `Source/NXVideo/NXVideoDrawArgs.h:23`
- Method count: `4`

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NXVideo.NXVideoDrawArgs
type_name: NXVideoDrawArgs
namespace: Pixoneer.NXDL.NXVideo
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
## InvalidatePtr
- Description: 연결된 비관리 객체를 무효화한다.
- Declaration: `Source/NXVideo/NXVideoDrawArgs.h:37`
- Implementation: `Source/NXVideo/NXVideoDrawArgs.cpp:89`

## SetPtr
- Description: 비관리 XVideoDrawArgs 포인터를 입력받아 내부 멤버를 초기화한다.
- Declaration: `Source/NXVideo/NXVideoDrawArgs.h:35`
- Implementation: `Source/NXVideo/NXVideoDrawArgs.cpp:75`

## SpaceToWorld
- Description: 현재 프레임에서 지구상의 지리공간(Space) 좌표를 비디오뷰 영상(World) 좌표로 변환한다.
- Declaration: `Source/NXVideo/NXVideoDrawArgs.h:44`, `Source/NXVideo/NXVideoDrawArgs.h:86`, `Source/NXVideo/NXVideoDrawArgs.h:122`, `Source/NXVideo/NXVideoDrawArgs.h:129`
- Implementation: `Source/NXVideo/NXVideoDrawArgs.cpp:207`, `Source/NXVideo/NXVideoDrawArgs.cpp:277`, `Source/NXVideo/NXVideoDrawArgs.cpp:341`, `Source/NXVideo/NXVideoDrawArgs.cpp:355`

## WorldToSpace
- Description: 현재 프레임에서 비디오뷰 영상(World) 좌표를 지구상의 지리공간(Space) 좌표로 변환한다.
- Declaration: `Source/NXVideo/NXVideoDrawArgs.h:52`, `Source/NXVideo/NXVideoDrawArgs.h:61`, `Source/NXVideo/NXVideoDrawArgs.h:69`, `Source/NXVideo/NXVideoDrawArgs.h:78`, `Source/NXVideo/NXVideoDrawArgs.h:93`, `Source/NXVideo/NXVideoDrawArgs.h:101`, `Source/NXVideo/NXVideoDrawArgs.h:108`, `Source/NXVideo/NXVideoDrawArgs.h:116`
- Implementation: `Source/NXVideo/NXVideoDrawArgs.cpp:220`, `Source/NXVideo/NXVideoDrawArgs.cpp:234`, `Source/NXVideo/NXVideoDrawArgs.cpp:252`, `Source/NXVideo/NXVideoDrawArgs.cpp:257`, `Source/NXVideo/NXVideoDrawArgs.cpp:290`, `Source/NXVideo/NXVideoDrawArgs.cpp:295`, `Source/NXVideo/NXVideoDrawArgs.cpp:316`, `Source/NXVideo/NXVideoDrawArgs.cpp:321`
