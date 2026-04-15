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
## Structured Page Facts
```yaml
page_family: retention_notes
role: curated_reference
verification_rules:
  - use_this_page_when_the_question_matches_its_scenario_scope
  - cross_check_methods_pages_before_emitting_exact_call_shapes
  - keep_output_shape_rules_from_this_page_when_present
```

## Runtime Usage
- Use this page as a richer scenario-level reference than the normalized `wf-*.md` pages when the question clearly matches this scenario.
- If this page defines output-shape constraints such as WPF/XAML delivery, keep those constraints in the final answer.
- Do not use sample-driven code patterns here to override conflicting exact signatures from methods pages.
