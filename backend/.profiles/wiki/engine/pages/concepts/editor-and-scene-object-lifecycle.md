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
