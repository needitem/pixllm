---
title: Annotation Editor API Workflow
description: Display, capture, edit, and reorder annotation objects on the editor canvas.
aliases:
  - editor api
  - neditor 사용법
  - annotation editor
  - 편집 화면 사용법
  - canvas editor
  - 편집 화면에 이미지를 표시
  - 편집 화면 화질개선 적용 이미지 도시
  - 편집 화면 이미지 파일 캡처
  - 편집 화면 확대 이미지 가져오기
  - 편집 화면 좌표계 설정
  - 편집 화면 zoom fit
  - 편집 화면 copy paste delete
  - 편집 화면 group ungroup undo redo
  - 편집 화면에 이미지를 표시
  - 편집 화면 확대 이미지 가져오기
  - 편집 화면 이미지 파일 캡처
  - 편집 화면에서 to front 변경하는 방법
  - 편집 화면에서 to rear 변경하는 방법
  - 편집 화면에서 to frontmost 변경하는 방법
  - 편집 화면에서 to rearmost 변경하는 방법
  - 편집 화면에서 component 사용하는 방법
  - 편집 화면에서 픽셀 to 실제 좌표 length 사용하는 방법
  - 편집 화면에서 영상 캡처하는 방법
symbols:
  - NEditor
tags:
  - engine
  - workflow
  - api
  - editor
---

# Overview
- Goal: answer `NEditor` usage questions from one page.
- This workflow covers image display/update, capture, SR and world/screen conversion, zoom/canvas state, and common editor actions such as copy/paste/group/delete.
- For the current wiki routing, use this family for annotation/editor canvas interactions, not for `scene object` file or selection lifecycle questions.
- For the current wiki routing, if the query explicitly says `편집 화면`, `Canvas`, `Component`, or editor z-order actions like `To Front/Rear/Frontmost/Rearmost`, route here before generic coordinate/view families.

## Primary Usage Buckets
- `이미지 표시/갱신`: `DisplayImage`, `DisplayImageWithoutThread`, `UpdateImage`, `UpdateImageEnhance`, `Unload`
- `캡처/확대 보기`: `CaptureImage`, `GetMagnifiedImage`
- `좌표계/화면 변환`: `SetSR`, `GetSR`, `ScreenToWorld`, `WorldToScreen`, `ConvPixelToWorldLength`, `ConvWorldToPixelLength`
- `편집 캔버스`: `SetCanvasSize`, `Resize`, `UpdateCanvas`, `SetWorld`, `SetWorldToCenter`, `SetWorldPerScreen`, `GetWorldPerScreen`
- `선택/편집`: `SelectAll`, `SelectNone`, `SetEditLayer`, `UpdateSelectedObjs`
- `객체 정리`: `Copy`, `Cut`, `Paste`, `Delete`, `Group`, `UnGroup`, `Undo`, `Redo`
- `Z-order 이동`: `MoveToFront`, `MoveToFrontmost`, `MoveToRear`, `MoveToRearmost`, `Up`, `Down`, `Left`, `Right`

## Practical Answer Shape
- `편집 화면에 이미지 표시`: 먼저 `DisplayImage*` 계열로 화면에 올리고, 후속 편집 작업은 `SetEditLayer`와 selection API로 연결합니다.
- `편집 화면 캡처`: `CaptureImage`와 `GetMagnifiedImage`를 구분해서 설명합니다. 전체 저장인지, 일부 확대 이미지인지 먼저 나눕니다.
- `편집 화면 좌표 변환`: 점 좌표는 `ScreenToWorld` / `WorldToScreen`, 길이 변환은 `ConvPixelToWorldLength` / `ConvWorldToPixelLength`를 우선 제시합니다.
- `편집 화면 순서 변경`: `MoveToFront*` / `MoveToRear*`는 객체 Z-order 이동, `Group/UnGroup`는 선택 집합 관리로 분리해서 답합니다.


## Answering Guidance
- Start with this workflow to confirm the question belongs to this API family before writing code or steps.
- Use the usage buckets and boundary notes to narrow the task to the smallest relevant slice.
- Read the linked howto, concept, and source pages from the Knowledge Bundle before giving a procedural answer.
- Use `Verified Facts` for exact method names and declarations; if this page is overview-only, say that and lean on the related pages for concrete steps.

## Knowledge Bundle
```yaml
concept_terms:
- editable object
- selection
- hit test
- edit lifecycle
routing_hints:
- all_of: [편집 화면, 영상 캡처]
- all_of: [편집 화면, to front]
- all_of: [편집 화면, component]
- all_of: [편집 화면, canvas]
- all_of: [편집 화면]
  any_of: [좌표계, 화면 좌표, 실제 좌표, 확대 이미지, group, ungroup, undo, redo]
bundle_pages:
- path: pages/howtos/editor-display-and-layer-editing.md
  relation: family_howto
- path: pages/concepts/editor-and-scene-object-lifecycle.md
  relation: family_concept
- path: pages/concepts/view-screen-world-coordinates.md
  relation: family_concept
- path: workflows/wf-api-imageview.md
  relation: dependency_workflow
```

<!-- GENERATED:RUNTIME_STATUS:START -->
## Runtime Ingest Status
- Auto-generated from raw source ingest at `2026-04-20T02:38:44Z`.
- Resolved required symbols: `0/0`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Verified Facts
```yaml
workflow_family: api_editor
output_shape: focused_snippet_or_helper
verification_rules:
  - use_this_workflow_as_primary_path
  - treat_this_page_as_source_backed_family_overview
notes:
  - Representative method names for NEditor are confirmed from dev3.0 API docs even though runtime methods index does not currently resolve this family.
```


