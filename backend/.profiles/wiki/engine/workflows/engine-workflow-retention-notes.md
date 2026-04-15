---
title: Engine Workflow Retention Notes
aliases:
  - Engine Workflow Retention Notes
  - engine-workflow-retention-notes
  - engine workflow retention notes
symbols:
  - NXImageView
  - NXVideoView
  - NXPlanetView
tags:
  - engine
  - workflow
  - retention
---

# Overview
- Existing workflow/example pages are curated scenario references and should be kept.
- New `wf-*.md` files are normalized atomic workflows used by the 360-question answer index.
- Temporary generation artifacts have been removed after the workflow/wiki files were accepted into the workspace.

# Keep
- `imageview-xdm-display-workflow.md`
- `nximageview-wpf-hosting.md`
- `nxdl-example-wpf-index.md`
- `xdl-datastructure-geoposition-wpf-examples.md`
- `xdl-imageview-wpf-examples.md`
- `xdl-milmapview-wpf-examples.md`
- `xdl-planetview-wpf-examples.md`
- `xdl-videoview-wpf-examples.md`
- all `wf-*.md` files

# Removed
- `engine_questions_360_ko.md`
- `backend/scripts/build_engine_question_workflows.py`

# Reasoning
- Existing pages are richer, scenario-driven, and already integrated with current wiki navigation.
- New workflow files are shorter and answer-routing oriented.
- Deleting older pages now would remove useful WPF/sample context.
- The removed files were generation-only artifacts, not user-facing workflow pages.
