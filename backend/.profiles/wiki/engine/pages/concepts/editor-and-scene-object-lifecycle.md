---
title: Editor and Scene Object Lifecycle
description: Cross-cutting concept page for editable objects, scene objects, and ownership transitions.
tags:
  - concept
  - editor
sources:
  - workflows/wf-api-editor.md
  - workflows/wf-api-scene-editor.md
---

# Editor and Scene Object Lifecycle

- Editor APIs answer how displayed objects are created, selected, moved, and updated.
- Scene-editor APIs answer how scene objects are loaded, saved, or transferred as durable scene content.
- This boundary matters because both families can mention visible objects, but only one owns edit interaction.
- In the current wiki routing, `편집 화면`, `canvas`, `group`, `undo`, or `to front` usually start in `Editor`.
- In the current wiki routing, `scene 파일`, `scene 객체`, `scene 선택`, or persistent scene IO belong to `Scene Editor`.
- Coordinate conversion inside Editor is documented here as `editor canvas interaction`; only explicit SR/code conversion should be answered from `Coordinate`.

## Answering Guidance
- Use this page to explain the shared idea or family boundary first.
- Route back to the owning workflow for exact API names, signatures, and code-level steps.
- Do not rely on this page alone when the answer needs executable call shapes.
