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

## Minimal C# Flow
Use this shape when the user asks how to convert image coordinates to ground/world coordinates. The `XSensorModel` must already be configured with the relevant sensor parameters; do not create placeholder sensor models in the sample.

```csharp
bool ProjectImageToWorldE(
    XSensorModel sensorModel,
    XVertex2d imagePoint,
    double height,
    out XVertex3d worldPoint)
{
    if (sensorModel == null)
    {
        worldPoint = null;
        return false;
    }

    return sensorModel.ImageToWorldE(imagePoint, height, out worldPoint);
}

bool ProjectImageToWorldG(
    XSensorModel sensorModel,
    XVertex2d imagePoint,
    double height,
    out XVertex3d geoPoint)
{
    if (sensorModel == null)
    {
        geoPoint = null;
        return false;
    }

    return sensorModel.ImageToWorldG(imagePoint, height, out geoPoint);
}
```

Use `ImageToWorldE` for Euclidean/world output and `ImageToWorldG` for geographic output. If the answer needs to mention sensor setup, state that `SetParamsLocal` or `SetParamsEarth` is the separate prerequisite rather than inventing setup values.

## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.

## Related Pages
- [Sensor Model API Workflow](../../workflows/wf-api-sensor-model.md)
- [Coordinate API Workflow](../../workflows/wf-api-coordinate.md)
- [Sensor Model and Projection](../concepts/sensor-model-and-projection.md)
