---
title: View Screen and World Coordinates
description: Cross-cutting concept page for screen-space and world-space transforms across view families.
tags:
  - concept
  - coordinates
sources:
  - workflows/wf-api-imageview.md
  - workflows/wf-api-videoview.md
  - workflows/wf-api-uspaceview.md
---

# View Screen and World Coordinates

- View families often expose both screen-space and world-space conversions.
- `ImageView`, `VideoView`, `MilmapView`, and `UspaceView` may all talk about cursor mapping, but they do not share the same rendering context.
- Use this page to explain the common idea, then route back to the owning family workflow for the exact API.
