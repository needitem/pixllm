# LLM Wiki Index

- Total pages: `68`
- Last rebuilt: `2026-04-27T01:07:38.455693+00:00`

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

- [Routing and Coverage Status](pages/analyses/routing-and-coverage-status.md) - Current routing quality and answer-material coverage status for the engine wiki.
- [TODO | Compiled Wiki Growth](pages/analyses/todo-compiled-wiki-growth.md) - Placeholder analysis page for the gap between current wiki-only answers and future accumulation.

## Decisions

- [Current Answer Policy](pages/decisions/current-answer-policy.md) - Current operating contract for engine answers with raw-source symbol ingest enabled and curated ingest still pending.

## Workflows

- [Annotation Editor API Workflow](workflows/wf-api-editor.md) - Display, capture, edit, and reorder annotation objects on the editor canvas.
- [Coordinate API Workflow](workflows/wf-api-coordinate.md) - Convert coordinate codes, define spatial references, and transform points between coordinate systems.
- [Core Utilities API Workflow](workflows/wf-api-core-utils.md) - Handle license validation, config path switching, and progress/helper utilities outside view families.
- [DFS Export API Workflow](workflows/wf-api-dfs.md) - Build DFS provider groups, run PBI/PBE exports, and track export progress or cancellation.
- [ImageView API Workflow](workflows/wf-api-imageview.md) - Host NXImageView, attach layers, control view state, and handle composite-linked display tasks.
- [MilmapView API Workflow](workflows/wf-api-milmapview.md) - Control MilmapView scale, center, render layers, capture, and map display state.
- [PlanetView API Workflow](workflows/wf-api-planetview.md) - Control PlanetView camera, render layers, dataset display, and capture operations.
- [Raster and XDM API Workflow](workflows/wf-api-raster.md) - Load raster files, fetch bands, build XDM composites, and tune display enhancement parameters.
- [Scene Editor API Workflow](workflows/wf-api-scene-editor.md) - Create, open, save, and select scene objects through the scene editor family.
- [Sensor Model API Workflow](workflows/wf-api-sensor-model.md) - Configure sensor parameters and project between image, world, and geographic coordinates.
- [UspaceView API Workflow](workflows/wf-api-uspaceview.md) - Control UspaceView render layers, space regions, camera state, and space/world/screen conversions.
- [Vector API Workflow](workflows/wf-api-vector.md) - Load vector files, inspect vector metadata, create geometry objects, and overlay them onto views.
- [VideoView API Workflow](workflows/wf-api-videoview.md) - Open video, bind opened video objects to views, capture frames, extract KLV, and explain embedded video-layer handling.

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
- [Raster Low-Level Parameter Recipes](pages/howtos/raster-low-level-parameter-recipes.md) - Common low-level raster operator tasks for input params, statistics, plateau values, masks, and feature seeds.
- [Raster Operator Parameter Families](pages/concepts/raster-operator-parameter-families.md) - Cross-cutting concept page for low-level raster operator names such as input params, statistics, plateaus, masks, and feature polygons.
- [Scene Editor Object IO Recipes](pages/howtos/scene-editor-object-io.md) - Common scene-editor tasks for scene-object creation, load, save, and object wiring.
- [Sensor Model Projection Recipes](pages/howtos/sensor-model-image-ground-projection.md) - Common sensor-model tasks for image-to-ground and ground-to-image projection.
- [Sensor Model and Projection](pages/concepts/sensor-model-and-projection.md) - Cross-cutting concept page for image-ground projection and sensor geometry.
- [Spatial Reference and Coordinate Transform](pages/concepts/spatial-reference-and-coordinate-transform.md) - Cross-cutting concept page for spatial reference setup and coordinate conversion.
- [UspaceView Render and World Recipes](pages/howtos/uspaceview-render-and-world.md) - Common UspaceView tasks for render-layer setup, world mapping, and interaction.
- [Vector Load and Overlay Recipes](pages/howtos/vector-load-and-overlay.md) - Common vector tasks for loading, styling, and overlaying vector content on views.
- [Video Channel, KLV, and Fusion](pages/concepts/video-channel-klv-and-fusion.md) - Cross-cutting concept page for video channel ownership, MPEG TS metadata, and fused video output.
- [Video Helper Processing Recipes](pages/howtos/video-helper-processing-recipes.md) - Common helper-class tasks for video filters, grouped channels, mosaics, and stabilizers.
- [VideoView Playback and KLV Recipes](pages/howtos/videoview-playback-and-klv.md) - Common video tasks for open, bind, render, capture, and KLV extraction.
- [View Screen and World Coordinates](pages/concepts/view-screen-world-coordinates.md) - Cross-cutting concept page for screen-space and world-space transforms across view families.