---
title: Coordinate Conversion Recipes
description: Common coordinate tasks for spatial reference creation, code lookup, and point transforms.
tags:
  - howto
  - coordinate
sources:
  - workflows/wf-api-coordinate.md
---

# Coordinate Conversion Recipes

## What This Recipe Covers
- Build or inspect `XSpatialReference` instances.
- Convert between Lat/Lon, UTM, and other supported coordinate-code forms.
- Use `XCoordinateTransformation` when the question is about transforming points between source and target SRs.

## Use This Recipe For
- The user asks how to convert WGS84 or Lat/Lon to UTM.
- The user asks how to determine zone codes or transform points.
- The user asks which coordinate object to create before feeding data to a view or editor.


## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.

## Related Pages
- [Coordinate API Workflow](../../workflows/wf-api-coordinate.md)
- [Spatial Reference and Coordinate Transform](../concepts/spatial-reference-and-coordinate-transform.md)
