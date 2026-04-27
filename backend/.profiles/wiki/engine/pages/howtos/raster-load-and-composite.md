---
title: Raster Load and Composite Recipes
description: Common raster workflows for load, band access, grayscale/RGB display, and enhancement setup.
tags:
  - howto
  - raster
  - xdm
sources:
  - workflows/wf-api-raster.md
  - workflows/wf-api-imageview.md
---

# Raster Load and Composite Recipes

## What This Recipe Covers
- Initialize `XRasterIO`, load files, and inspect subdatasets before selecting bands.
- Use `XRSLoadFile.GetBandAt` to fetch bands for grayscale or RGB composition.
- Assemble `XDMComposite` and register it through `XDMCompManager`.
- Tune cut and stretch before handing the composite to `ImageView`.

## Minimal C# Flow
Use this shape when the user asks how to load an XDM/raster file and display it through an `NXImageLayerComposites` layer.

```csharp
XRasterIO rasterIO = new XRasterIO();
string error = "";
if (!rasterIO.Initialize(out error))
    return;

XRSLoadFile xrsFile = rasterIO.LoadFile(xdmPath, out error, true, eIOCreateXLDMode.All_NoMsg);

NXImageLayerComposites compLayer = new NXImageLayerComposites();
XDMCompManager manager = compLayer.GetXDMCompManager();

XDMComposite comp = new XDMComposite();
comp.Name = xrsFile.FileName;

if (xrsFile.NumBand >= 3)
{
    XDMBand b0 = xrsFile.GetBandAt(0);
    XDMBand b1 = xrsFile.GetBandAt(1);
    XDMBand b2 = xrsFile.GetBandAt(2);

    comp.Mode = eCompMode.RGB;
    comp.SetBand(ref b0, (eCompBandIdx)2);
    comp.SetBand(ref b1, (eCompBandIdx)1);
    comp.SetBand(ref b2, (eCompBandIdx)0);
}
else
{
    XDMBand b0 = xrsFile.GetBandAt(0);
    comp.Mode = eCompMode.Gray;
    comp.SetBand(ref b0, (eCompBandIdx)0);
}

manager.AddXDMComposite(ref comp);
NXImageLayer imageLayer = compLayer as NXImageLayer;
imageView.AddImageLayer(ref imageLayer);

imageView.ZoomFit();
compLayer.Invalidate();
imageView.RefreshScreen();
```

## Use This Recipe For
- The user asks how to load GeoTiff, XDM, or raw raster files.
- The user asks how to switch between grayscale and color display.
- The user asks how to improve displayed raster quality.

## Display Quality / Enhancement Flow
Use the existing `XDMComposite` reference that was created and registered earlier. Do not look for quality setters on `NXImageView`, and do not invent a manager index getter to recover the composite; display enhancement belongs to the composite object you already have. Do not state numeric value ranges unless source evidence gives the range.

```csharp
void ApplyDisplayQuality(NXImageView imageView, XDMComposite comp)
{
    if (comp == null)
        return;

    comp.SetBrightness(brightnessValue);   // int
    comp.SetContrast(contrastValue);       // int
    comp.SetSaturation(saturationValue);   // int
    comp.SetColorBalance(redBalance, greenBalance, blueBalance);

    for (int band = 0; band < 3; band++)
    {
        comp.SetGammaValue(gammaValue, band);
    }

    comp.InterpolPixel = true;
    comp.InterpolByCubic = true;

    imageView.RefreshScreen();
}
```

Only use stretch/cut enum literals when they appear in source evidence for the specific answer. If no literal is confirmed, show the method family without executable enum-placeholder code.

```csharp
void ApplyStretchAndCut(XDMComposite comp, eCompStretchType stretchType, eCompStretchCoverage coverage, eCompCutType cutType)
{
    if (comp == null)
        return;

    for (int band = 0; band < 3; band++)
    {
        comp.SetStretchType(stretchType, band);
        comp.SetStretchCoverage(coverage, band);
        comp.SetCutType(cutType, band);
    }
}
```

For gamma-style display, set the per-band gamma value on the existing `XDMComposite`.

```csharp
if (comp == null)
    return;

for (int band = 0; band < 3; band++)
{
    comp.SetGammaValue(gammaValue, band); // double
}

imageView.RefreshScreen();
```

For enlarged display interpolation, set the properties on `XDMComposite`, not on `NXImageView`.

```csharp
comp.InterpolPixel = true;
comp.InterpolByCubic = true;

compLayer.Invalidate();
imageView.RefreshScreen();
```


## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.
- For XDM/ImageView display questions, do not say the ImageView display step is missing when `NXImageLayerComposites.GetXDMCompManager`, `XDMCompManager.AddXDMComposite`, and `NXImageView.AddImageLayer` are available in evidence.
- Use `XRasterIO.LoadFile` for normal XDM/GeoTiff/raster files. Use `LoadRawFile` only for explicit raw raster parameter workflows.
- For ordinary XDM/ImageView display, keep the short `LoadFile(xdmPath, out error, true, eIOCreateXLDMode.All_NoMsg)` overload from the minimal flow; do not expand it to the subdataset/thread overload unless the user asks about subdatasets.
- Do not invent convenience APIs such as `LoadXDMFile`, `OpenXDM`, `SetData`, `Band`, or `NXImageLayer(loadedFile)`.

## Common Recipes
- `GeoTiff/XDM 로드`
  A typical raster flow is `Initialize`, then `LoadFile`, then inspect subdatasets or fetch bands with `GetBandAt`.
- `raw raster 로드`
  Use `LoadRawFile` only when the question is about explicit raw data parameters rather than normal file formats.
- `흑백/칼라 도시`
  A typical composite explanation chooses bands, then calls `SetBand` with `(eCompBandIdx)0/1/2`, then registers the composite with `AddXDMComposite`. Do not invent `eCompBandIdx.Red/Green/Blue` members unless a source snippet explicitly shows them.
- `합성 순서 바꾸기`
  Use `MoveComposite` or remove/re-add composites when the question is about stacking or visible ordering.
- `stretch/cut`
  Group `SetCutType`, `SetStretchType`, `SetStretchCoverage`, `SetCutMin`, and `SetCutMax` into one explanation instead of listing them separately.
- `gamma/brightness/contrast/saturation/color balance`
  Use `SetGammaValue`, `SetBrightness`, `SetContrast`, `SetSaturation`, and `SetColorBalance` on `XDMComposite`; do not invent `SetGamma` or `SetStretch`.
- `interpolation`
  Use `XDMComposite.InterpolPixel` and `XDMComposite.InterpolByCubic`; do not invent `NXImageView.SetInterpolationType`.

## Related Pages
- [Raster and XDM API Workflow](../../workflows/wf-api-raster.md)
- [ImageView API Workflow](../../workflows/wf-api-imageview.md)
- [Raster Band and Enhancement Model](../concepts/raster-band-and-enhancement.md)
