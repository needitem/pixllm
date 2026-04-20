# LLM Wiki Index

- Total pages: `64`
- Last rebuilt: `2026-04-20T00:52:19.508956+00:00`

## Coordination

- [README.md](README.md)
- [SCHEMA.md](SCHEMA.md)
- [log.md](log.md)
- [pages/home.md](pages/home.md)

## Sources

- [Raw Source Root](pages/sources/raw-source-root.md) - Canonical immutable raw source tree used for runtime symbol ingest and future curated ingest work.
- [Source Module | NXDL](pages/sources/nxdl.md) - Auto-generated summary for raw source module `NXDL`.
- [Source Module | NXDLMilSymbol](pages/sources/nxdlmilsymbol.md) - Auto-generated summary for raw source module `NXDLMilSymbol`.
- [Source Module | NXDLcc](pages/sources/nxdlcc.md) - Auto-generated summary for raw source module `NXDLcc`.
- [Source Module | NXDLdfs](pages/sources/nxdldfs.md) - Auto-generated summary for raw source module `NXDLdfs`.
- [Source Module | NXDLgr](pages/sources/nxdlgr.md) - Auto-generated summary for raw source module `NXDLgr`.
- [Source Module | NXDLio](pages/sources/nxdlio.md) - Auto-generated summary for raw source module `NXDLio`.
- [Source Module | NXDLncw](pages/sources/nxdlncw.md) - Auto-generated summary for raw source module `NXDLncw`.
- [Source Module | NXDLrs](pages/sources/nxdlrs.md) - Auto-generated summary for raw source module `NXDLrs`.
- [Source Module | NXDLrsEx](pages/sources/nxdlrsex.md) - Auto-generated summary for raw source module `NXDLrsEx`.
- [Source Module | NXDLsar](pages/sources/nxdlsar.md) - Auto-generated summary for raw source module `NXDLsar`.
- [Source Module | NXDLscene](pages/sources/nxdlscene.md) - Auto-generated summary for raw source module `NXDLscene`.
- [Source Module | NXDLsm](pages/sources/nxdlsm.md) - Auto-generated summary for raw source module `NXDLsm`.
- [Source Module | NXDLvc](pages/sources/nxdlvc.md) - Auto-generated summary for raw source module `NXDLvc`.
- [Source Module | NXDLwnd](pages/sources/nxdlwnd.md) - Auto-generated summary for raw source module `NXDLwnd`.
- [Source Module | NXEasy3D](pages/sources/nxeasy3d.md) - Auto-generated summary for raw source module `NXEasy3D`.
- [Source Module | NXImage](pages/sources/nximage.md) - Auto-generated summary for raw source module `NXImage`.
- [Source Module | NXMilmap](pages/sources/nxmilmap.md) - Auto-generated summary for raw source module `NXMilmap`.
- [Source Module | NXPlanet](pages/sources/nxplanet.md) - Auto-generated summary for raw source module `NXPlanet`.
- [Source Module | NXUspace](pages/sources/nxuspace.md) - Auto-generated summary for raw source module `NXUspace`.
- [Source Module | NXVideo](pages/sources/nxvideo.md) - Auto-generated summary for raw source module `NXVideo`.

## Topics

- [TODO | Raw Source Ingest](pages/topics/todo-raw-source-ingest.md) - Remaining work for extending raw-source ingest beyond the runtime methods index.

## Analyses

- [TODO | Compiled Wiki Growth](pages/analyses/todo-compiled-wiki-growth.md) - Placeholder analysis page for the gap between current wiki-only answers and future accumulation.

## Decisions

- [Current Answer Policy](pages/decisions/current-answer-policy.md) - Current operating contract for engine answers with raw-source symbol ingest enabled and curated ingest still pending.

## Workflows

- [Annotation Editor API Workflow](workflows/wf-api-editor.md) - # Overview - Goal: answer `NEditor` usage questions from one page. - This workflow covers image display/update, capture, SR and world/screen conversion, zoom/canvas state, and common editor actions such as copy/paste/group/delete. - Prefer
- [Coordinate API Workflow](workflows/wf-api-coordinate.md) - # Overview - Goal: answer most coordinate-system questions from one page. - This workflow covers `Xcc` code conversion, `XCoordinateTransformation`, and `XSpatialReference`. - Prefer this family for SR/code conversion and explicit coordinat
- [Core Utilities API Workflow](workflows/wf-api-core-utils.md) - # Overview - Goal: collect common top-level NXDL utilities that users call directly outside a view family. - This workflow covers progress reporting, config-path switching, and license validation. ## Knowledge Bundle
- [DFS Export API Workflow](workflows/wf-api-dfs.md) - # Overview - Goal: register DFS providers and build PBI/PBE outputs. - Prefer this family for DFS provider-group registration, PBI/PBE export, export progress polling, and export cancel flows. ## Knowledge Bundle
- [ImageView API Workflow](workflows/wf-api-imageview.md) - # Overview - Goal: answer most `NXImageView` usage questions from one page. - Default host context: WPF. `NXImageView` is a WinForms-backed control, so host it through `WindowsFormsHost` when the shell matters. - This workflow covers host s
- [MilmapView API Workflow](workflows/wf-api-milmapview.md) - # Overview - Goal: cover scale, center, render-layer attach/order, draw args, and capture on `NXMilmapView`. - This workflow is the primary family for normal `MilmapView` usage questions. - If `MilmapView` is explicitly named, prefer this f
- [PlanetView API Workflow](workflows/wf-api-planetview.md) - # Overview - Goal: cover camera, layer attach/order, capture, and dataset registration on `NXPlanetView`. - This workflow merges view control and PBI dataset usage into one API family page. - If `PlanetView` is explicitly named, prefer this
- [Raster and XDM API Workflow](workflows/wf-api-raster.md) - # Overview - Goal: cover raster-file load, band access, XDM composite assembly, and display-quality tuning. - This workflow is the primary family for `XRasterIO`, `XRSLoadFile`, `XDMBand`, `XDMComposite`, and `XDMCompManager`. - Prefer this
- [Scene Editor API Workflow](workflows/wf-api-scene-editor.md) - # Overview - Goal: create/open/save scenes and select scene objects through `NXPlanetLayerSceneEditor`. - This workflow merges scene IO and selection into one API family page. - Prefer this family when the question explicitly says `scene`,
- [Sensor Model API Workflow](workflows/wf-api-sensor-model.md) - # Overview - Goal: configure sensor parameters and project between image and world spaces. - Prefer this family for image-to-ground, ground-to-image, image-to-geo, geo-to-image, and image-center map-coordinate questions. ## Knowledge Bundle
- [UspaceView API Workflow](workflows/wf-api-uspaceview.md) - # Overview - Goal: define region, camera, SR, and interaction mode on `NXUspaceView`. - Prefer this family for `UspaceView`-named coordinate or space/screen conversion questions. - If the question explicitly names `UspaceView`, prefer this
- [Vector API Workflow](workflows/wf-api-vector.md) - # Overview - Goal: load vector data, inspect metadata, create vector objects, and overlay them on image or map views. - Prefer this family for `vector`, `shp`, `overlay`, `bounding box`, `vertex`, `property`, and vector-layer hit-test quest
- [VideoView API Workflow](workflows/wf-api-videoview.md) - # Overview - Goal: cover open/bind/render/capture/KLV questions for the video family. - This workflow covers `XVideoIO`, `NXVideoView`, `NXImageLayerVideo`, and `NXMpegTSAnalysis`. - Even when `ImageView` is explicitly named, prefer this fa

## Other

- [Coordinate Conversion Recipes](pages/howtos/coordinate-conversion-recipes.md) - Common coordinate tasks for spatial reference creation, code lookup, and point transforms.
- [Core Utils File and System Recipes](pages/howtos/core-utils-file-and-system.md) - Common core-utils tasks for filesystem, string, process, and helper APIs.
- [DFS Provider and Dataset Recipes](pages/howtos/dfs-provider-and-dataset.md) - Common DFS tasks for provider setup, dataset registration, and lookup.
- [Editor Display and Layer Editing Recipes](pages/howtos/editor-display-and-layer-editing.md) - Common editor tasks for displayed objects, selection, editing, and coordinate interaction.
- [Editor and Scene Object Lifecycle](pages/concepts/editor-and-scene-object-lifecycle.md) - Cross-cutting concept page for editable objects, scene objects, and ownership transitions.
- [Engine Core Utility Scope](pages/concepts/engine-core-utility-scope.md) - Cross-cutting concept page for separating core utility usage from domain-family APIs.
- [ImageView Display Recipes](pages/howtos/imageview-display-recipes.md) - Common ImageView tasks for loading, attaching layers, fitting view, and reading pixel values.
- [Layer, Composite, and Display Pipeline](pages/concepts/layer-composite-display-pipeline.md) - Cross-cutting concept page for how loaded data becomes one or more visible layers.
- [MilmapView Display and Video Recipes](pages/howtos/milmapview-display-and-video.md) - Common MilmapView tasks for layer display, camera control, and video layer wiring.
- [PlanetView Dataset and Camera Recipes](pages/howtos/planetview-dataset-and-camera.md) - Common PlanetView tasks for datasets, camera movement, and layer display.
- [Provider, Dataset, and Scene Assets](pages/concepts/provider-dataset-and-scene-assets.md) - Cross-cutting concept page for providers, datasets, and scene asset routing.
- [Raster Band and Enhancement Model](pages/concepts/raster-band-and-enhancement.md) - Cross-cutting concept page for band access, grayscale/RGB composition, and display enhancement.
- [Raster Load and Composite Recipes](pages/howtos/raster-load-and-composite.md) - Common raster workflows for load, band access, grayscale/RGB display, and enhancement setup.
- [Scene Editor Object IO Recipes](pages/howtos/scene-editor-object-io.md) - Common scene-editor tasks for scene-object creation, load, save, and object wiring.
- [Sensor Model Projection Recipes](pages/howtos/sensor-model-image-ground-projection.md) - Common sensor-model tasks for image-to-ground and ground-to-image projection.
- [Sensor Model and Projection](pages/concepts/sensor-model-and-projection.md) - Cross-cutting concept page for image-ground projection and sensor geometry.
- [Spatial Reference and Coordinate Transform](pages/concepts/spatial-reference-and-coordinate-transform.md) - Cross-cutting concept page for spatial reference setup and coordinate conversion.
- [UspaceView Render and World Recipes](pages/howtos/uspaceview-render-and-world.md) - Common UspaceView tasks for render-layer setup, world mapping, and interaction.
- [Vector Load and Overlay Recipes](pages/howtos/vector-load-and-overlay.md) - Common vector tasks for loading, styling, and overlaying vector content on views.
- [Video Channel, KLV, and Fusion](pages/concepts/video-channel-klv-and-fusion.md) - Cross-cutting concept page for video channel ownership, MPEG TS metadata, and fused video output.
- [VideoView Playback and KLV Recipes](pages/howtos/videoview-playback-and-klv.md) - Common video tasks for open, bind, render, capture, and KLV extraction.
- [View Screen and World Coordinates](pages/concepts/view-screen-world-coordinates.md) - Cross-cutting concept page for screen-space and world-space transforms across view families.