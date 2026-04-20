---
title: Sensor Model Projection Recipes
description: Common sensor-model tasks for image-to-ground and ground-to-image projection.
tags:
  - howto
  - sensor-model
sources:
  - workflows/wf-api-sensor-model.md
  - workflows/wf-api-coordinate.md
---

# Sensor Model Projection Recipes

## What This Recipe Covers
- Explain image-to-ground and ground-to-image projection flows.
- Clarify when the user needs a sensor model rather than only a coordinate transform.

## Use This Recipe For
- The user asks how to project image points to ground coordinates.
- The user asks how sensor geometry participates in positioning or view alignment.


## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.

## Related Pages
- [Sensor Model API Workflow](../../workflows/wf-api-sensor-model.md)
- [Coordinate API Workflow](../../workflows/wf-api-coordinate.md)
- [Sensor Model and Projection](../concepts/sensor-model-and-projection.md)
