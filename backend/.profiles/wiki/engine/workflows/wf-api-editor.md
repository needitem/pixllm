---
title: Annotation Editor API Workflow
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
- Prefer this family for annotation/editor canvas interactions, not for `scene object` file or selection lifecycle questions.
- If the query explicitly says `편집 화면`, `Canvas`, `Component`, or editor z-order actions like `To Front/Rear/Frontmost/Rearmost`, prefer this family over generic coordinate/view families.

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
- Auto-generated from raw source ingest at `2026-04-20T00:52:13Z`.
- Resolved required symbols: `0/0`
- Missing required symbols: `0`
<!-- GENERATED:RUNTIME_STATUS:END -->
## Required Facts
```yaml
workflow_family: api_editor
output_shape: focused_snippet_or_helper
verification_rules:
  - use_this_workflow_as_primary_path
  - treat_this_page_as_source_backed_family_overview
```

