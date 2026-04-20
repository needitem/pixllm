---
title: Raster Low-Level Parameter Recipes
description: Common low-level raster operator tasks for input params, statistics, plateau values, masks, and feature seeds.
tags:
  - howto
  - raster
  - low-level
sources:
  - workflows/wf-api-raster.md
---

# Raster Low-Level Parameter Recipes

## What This Recipe Covers
- Low-level `XDMBand*` operator questions where the user names a parameter or intermediate value instead of the family.
- Input Param, Color Table, Statistics, Plateau, Mask Polygon, Feature From Seed Polygon, and similar operator-side parameters.

## Use This Recipe For
- The user asks about raster processing parameters but does not clearly name the owning class.
- The user asks about EO/IR, IR filter, mosaic LT, feature extraction, geo-correction, or other advanced raster operators.

## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the user is actually asking about coordinate conversion or vector geometry, say so and route out instead of forcing everything into raster.

## Common Recipes
- `EOIR / Input Param`
  Use the operator-specific `GetInputParam` / `SetInputParam` pair before explaining the actual fusion or filter call.
- `IR Filter / Plateau / Statistics`
  Group `CalcStatistics`, `CreateHistogram`, `Calcplateau`, and `SetPlateauValue` together as one IR-filter tuning flow.
- `Feature Extraction`
  Use `ExtractFeatureFromSeedPixel` or `ExtractFeatureFromSeedPolygon` when the question is about seed-driven feature growth, and keep polygon handling inside the raster operator unless the user is editing standalone vector geometry.
- `Geo Correct / Image-Map Points`
  If the user names image/world point conversion inside a raster operator, answer from the raster operator first and only route to `Sensor Model` or `Coordinate` if the question becomes pure projection logic.
- `Mosaic LT / Mask Polygon`
  Use `SetMaskPolygon`, `SetMaskPolygonMode`, and `RemoveMaskAllPolygons` when the question is about mosaic masking rather than vector overlay.

## Related Pages
- [Raster and XDM API Workflow](../../workflows/wf-api-raster.md)
- [Raster Band and Enhancement Model](../concepts/raster-band-and-enhancement.md)
- [Raster Operator Parameter Families](../concepts/raster-operator-parameter-families.md)
