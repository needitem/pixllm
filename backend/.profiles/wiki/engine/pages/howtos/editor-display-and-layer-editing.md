---
title: Editor Display and Layer Editing Recipes
description: Common editor tasks for displayed objects, selection, editing, and coordinate interaction.
tags:
  - howto
  - editor
sources:
  - workflows/wf-api-editor.md
  - workflows/wf-api-imageview.md
---

# Editor Display and Layer Editing Recipes

## What This Recipe Covers
- Create and manage editable objects shown in a view.
- Explain selection, hit testing, and edit-state transitions.
- Clarify when a question belongs to the Editor family rather than plain ImageView display.
- Distinguish image display/update, coordinate conversion, capture, z-order, and selection as separate tasks.

## Use This Recipe For
- The user asks how to select, move, or edit objects on top of imagery.
- The user asks about displayed annotations or edit interactions.
- The user asks how to capture the editor canvas, get a magnified image, or convert editor screen/world lengths.

## Minimal C# Flow
Use this shape when the user asks about `NEditor` copy/paste/delete or edit-object operations.
`NEditor` is the answer surface for these questions; do not replace it with `NXImageLayerVectorEditor` unless the user explicitly names that class.
Assume the `NEditor` control and the editable `NanLayer` are already available when the question is about edit commands rather than file loading.

Source-backed NEditor signatures for this flow:
- `public partial class NEditor : System.Windows.Controls.UserControl`
- `public void SetEditLayer(NanLayer layer)`
- `public void SelectAll()`
- `public void SelectNone()`
- `public void UpdateSelectedObjs()`
- `public void Copy()`
- `public void Paste()`
- `public void Delete()`

```csharp
NEditor editor = existingEditor;
NanLayer editLayer = existingLayer;

editor.SetEditLayer(editLayer);

// SelectAll is one confirmed way to make the target set explicit.
// For mouse/UI selection flows, the current selected objects are used.
editor.SelectAll();
editor.UpdateSelectedObjs();

editor.Copy();
editor.Paste();
editor.Delete();
```

For partial selection flows, keep `SelectAll()` out and call `Copy`, `Paste`, or `Delete` on the current editor selection.
Do not invent helper getters such as `GetTargetLayer()` or availability checks such as `CanPaste()` for `NEditor`.

## Answering Guidance
- Start from the owning workflow, then use this page to turn that family-level context into ordered task steps.
- Prefer step-oriented answers that name the concrete API surface already verified by the workflow page.
- If the task crosses families, say which dependency workflow should be read next instead of guessing from this page alone.

## Common Recipes
- `편집 화면에 이미지 표시`
  A typical explanation starts with `DisplayImage` or `DisplayImageWithoutThread`, and then introduces `SetEditLayer` if the next step is object editing rather than read-only display.
- `편집 화면 갱신`
  Use `UpdateImage`, `UpdateImageEnhance`, or `UpdateCanvas` depending on whether the raster, enhancement result, or object canvas changed.
- `편집 화면 캡처`
  Use `CaptureImage` for saved output and `GetMagnifiedImage` when the user wants an enlarged cutout of the current view.
- `편집 화면 좌표 변환`
  Use `ScreenToWorld` / `WorldToScreen` for point mapping, and `ConvPixelToWorldLength` / `ConvWorldToPixelLength` for scale/length questions.
- `선택과 정렬`
  Use `SelectAll`, `SelectNone`, `UpdateSelectedObjs`, then `MoveToFront*` / `MoveToRear*` for z-order changes.
- `편집 객체 관리`
  Use `Copy`, `Cut`, `Paste`, `Delete`, `Group`, `UnGroup`, `Undo`, and `Redo` as the core editing set.

## Related Pages
- [Editor API Workflow](../../workflows/wf-api-editor.md)
- [ImageView API Workflow](../../workflows/wf-api-imageview.md)
- [Editor and Scene Object Lifecycle](../concepts/editor-and-scene-object-lifecycle.md)
