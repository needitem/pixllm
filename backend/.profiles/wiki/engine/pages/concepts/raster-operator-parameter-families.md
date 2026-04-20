---
title: Raster Operator Parameter Families
description: Cross-cutting concept page for low-level raster operator names such as input params, statistics, plateaus, masks, and feature polygons.
tags:
  - concept
  - raster
  - low-level
sources:
  - workflows/wf-api-raster.md
---

# Raster Operator Parameter Families

- Many low-level raster questions name an operator parameter rather than the owning family.
- In the current wiki routing, names such as `Input Param`, `Color Table`, `Statistics`, `Plateau`, `Mask Polygon`, or `Feature From Seed Polygon` are treated as raster-operator questions, not core-utils or coordinate questions.
- If the parameter belongs to an `XDMBand*` operator, keep the answer in the raster family unless the user explicitly shifts into vector geometry or coordinate-system conversion.

## Answering Guidance
- Use this page to explain the shared pattern first: low-level operator parameters still belong to raster processing.
- Route back to the owning workflow for exact API names, signatures, and code-level steps.
- Do not rely on this page alone when the answer needs executable call shapes.
